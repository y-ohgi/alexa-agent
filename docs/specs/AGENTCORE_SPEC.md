# AgentCore 活用仕様 (AGENTCORE_SPEC)

| 項目 | 内容 |
| --- | --- |
| ステータス | Draft |
| 最終更新日 | 2026-07-13 |
| 関連仕様 | [ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md), [AUTH_SPEC.md](./AUTH_SPEC.md), [API_SPEC.md](./API_SPEC.md) |

## 概要

本プロダクトは Amazon Bedrock AgentCore の各機能を**学習を兼ねてフル活用**する。
この仕様書は AgentCore の各コンポーネントを整理し、本プロダクトでの用途・採用フェーズ・
主要な制約を一覧化する。個別の構成・認証・対話仕様は関連仕様書に委ねる。

> **前提**: AgentCore は 2025-10-13 に GA。コンシューム課金(ハーネス自体は無料、
> 消費した基盤リソース分のみ課金)。東京リージョン(ap-northeast-1)を含む 9 リージョンで提供。
> 本プロダクトは TypeScript を採用し、AgentCore の **Node.js/TypeScript ネイティブ対応**
> (`bedrock-agentcore` npm、`@aws/agentcore` CLI、`aws-cdk-lib/aws-bedrockagentcore` L2)を用いる。

## 背景・目的

- AgentCore の全機能を触れる構成にすることで、チームとして AgentCore の設計思想と運用を習得する
- ただし一度に全部は使わず、**MVP → Phase 2 → Phase 3 と段階的に採用**し、
  各段階で「なぜその機能が必要か」を明確にする

## 仕様(確定事項)

### コンポーネント別の採用方針

| # | AgentCore コンポーネント | 本プロダクトでの用途 | 採用フェーズ |
| --- | --- | --- | --- |
| 1 | **Runtime** | Mastra エージェント本体のサーバーレス実行基盤 | **MVP** |
| 2 | **Identity** | Inbound(Lambda→Runtime の JWT 認証)/ 将来は Outbound・エンドユーザー認可 | **MVP**(Inbound)/ Phase 2・3 |
| 3 | **Memory** | 短期記憶(セッション内文脈)。将来は長期記憶(嗜好・要約) | **MVP**(短期)/ Phase 3(長期) |
| 4 | **Observability** | トレース・メトリクス・ログ(CloudWatch GenAI Observability) | **MVP** |
| 5 | **Gateway** | 外部 API/Lambda を MCP ツール化してエージェントに公開 | Phase 2 |
| 6 | **Code Interpreter** | サンドボックスでのコード実行(計算・データ処理) | Phase 2(学習用途で早期に試す) |
| 7 | **Browser Tool** | マネージド Headless Chrome によるウェブ操作 | Phase 3 |

> Policy / Evaluations / Optimization / Web Search / Agent Registry / Payments 等の追加機能は
> 現時点では対象外。学習が進んだ段階で Open Questions として再検討する。

### 1. Runtime(MVP)

- **サービス契約**: コンテナが **port 8080** で `POST /invocations`(本体)と `GET /ping`(ヘルスチェック)を提供。**linux/arm64 (Graviton) 必須**。
- Mastra エージェントを **`bedrock-agentcore` npm の `BedrockAgentCoreApp`** でラップし、上記契約を満たす HTTP サーバとして起動する(公式 Mastra × AgentCore デプロイガイド準拠)。
- **セッション分離**: セッションごとに専用 microVM(CPU/メモリ/FS 隔離)。状態はエフェメラル(永続化は Memory で行う)。
- **セッション寿命**: アイドル 15 分 / 最大 8 時間で終了。`runtimeSessionId` は UUID 推奨。
- **バージョン/エンドポイント**: 作成時に V1 + DEFAULT エンドポイント。設定変更ごとに不変バージョンが増える。dev/prod でエンドポイントを分けられる。
- **呼び出し**: `InvokeAgentRuntime`(payload 最大 100MB、SSE ストリーミング可)。
- コンテナ内では**非 root・読み取り専用**で動くため、Mastra 既定のファイルベースストレージ(LibSQL/`./mastra.db`)は無効化する(公式ガイドの gotcha)。

### 2. Identity(MVP: Inbound)

- **Inbound Auth** は「IAM SigV4」か「OAuth JWT」の**排他選択**。本プロダクトは [AUTH_SPEC.md](./AUTH_SPEC.md) の方針に従い **Cognito の JWT(M2M)** を採用。
  - 重要な制約: **OAuth JWT を使う場合、`InvokeAgentRuntime` を AWS SDK では呼べず、生の HTTPS リクエストが必要**。
- **Workload Identity** は Runtime デプロイ時に自動作成される。
- **Outbound Auth / Token Vault**(Phase 2): 外部サービスの OAuth(2LO/3LO)・API キーを Token Vault で管理。Gateway/ツール連携で活用。
- 詳細は [AUTH_SPEC.md](./AUTH_SPEC.md)。

### 3. Memory(MVP: 短期 / Phase 3: 長期)

- **短期記憶(MVP)**: 会話ターンを `CreateEvent` で **event** として保存し、`ListEvents` で取得。セッション内のマルチターン文脈維持に使用。
  - モデル: `actorId`(エンドユーザー)/ `sessionId`(会話)。MVP では Alexa の識別子からマッピング。
- **長期記憶(Phase 3)**: 非同期で event から insight を抽出する **strategy** を有効化。
  - `Summary`(セッション要約)、`UserPreference`(嗜好)、`Semantic`(事実)を想定。
  - `RetrieveMemoryRecords`(セマンティック検索)で関連記憶を取得。
  - **namespace**(末尾スラッシュ付きの階層パス、`{actorId}`/`{sessionId}` 変数)でマルチテナント分離。IAM の `bedrock-agentcore:namespace` 条件キーで制御可能。
- 課金: 短期 $0.25/1,000 events、長期保存 $0.75/1,000 records・月、長期取得 $0.50/1,000 calls。

### 4. Observability(MVP)

- **OTEL ネイティブ**。Runtime ホスト型エージェントは**自動計装**(Node.js は ADOT Node.js パッケージ)。追加コード不要。
- **前提設定(アカウント単位で一度)**: **CloudWatch Transaction Search を有効化**(spans を `aws/spans` に流す)。これを忘れるとトレースが見えない。
- **CloudWatch GenAI Observability** ダッシュボードで Agents / Sessions / Traces ビューを確認。
- 主なメトリクス(namespace `bedrock-agentcore`): Invocations / Throttles / Errors / Latency / SessionCount / ActiveSessionCount など。
- OTEL baggage の `session.id` でセッションを相関。

### 5. Gateway(Phase 2)

- 既存 API/Lambda/OpenAPI/Smithy を**ゼロコードで MCP ツール化**するマネージド MCP サーバ。
- ターゲット種別: MCP ターゲット(集約モード・セマンティックツール検索・3LO 対応)/ HTTP ターゲット / Inference ターゲット。
- Inbound(Gateway Authorizer): OAuth(JWT)/ IAM / authenticate-only / no-auth。
- Outbound(Credential Provider): 実行ロール / API キー / OAuth(Token Vault 連携)。
- 本プロダクトでは天気・カレンダー等の外部 API をツール化する用途を想定([OVERVIEW_SPEC.md](./OVERVIEW_SPEC.md) の Phase 2)。

### 6. Code Interpreter(Phase 2 / 学習用途で早期に試す)

- Python/JavaScript/**TypeScript** 対応のサンドボックス実行環境(セッション隔離)。
- ファイル: インライン 100MB / S3 経由 5GB。実行時間: 既定 15 分〜最大 8 時間。
- 計算・データ処理をエージェントに安全に行わせる用途。学習目的で MVP 直後に PoC する。

### 7. Browser Tool(Phase 3)

- マネージド Headless Chrome。Playwright/Strands/Nova Act で操作。Live View(人間介入)・セッション録画(S3)対応。
- API のないウェブ操作・フォーム入力・スクリーンショットによる視覚理解などに使用。

## 未確定事項 (Open Questions)

- [ ] リージョン: 東京(ap-northeast-1)で確定してよいか(AgentCore・Bedrock モデルの提供状況を要確認)
- [ ] Inbound 認証を Cognito JWT のままにするか、MVP は IAM SigV4 で簡素化するか([AUTH_SPEC.md](./AUTH_SPEC.md) の Open Question と連動)
- [ ] Memory 短期記憶を MVP で AgentCore Memory に載せるか、まずは Runtime セッション内文脈のみで足りるか(コストと学習価値のトレードオフ)
- [ ] Code Interpreter を Phase 2 のどのユースケースで使うか(学習 PoC のテーマ)
- [ ] Runtime のデプロイを `@aws/agentcore` CLI 中心にするか、CDK(`aws-bedrockagentcore` L2 のコンテナ artifact)中心にするか([ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md) と連動)

## 変更履歴

| 日付 | 変更内容 |
| --- | --- |
| 2026-07-13 | 初版作成(AgentCore 全機能の採用方針を整理) |
