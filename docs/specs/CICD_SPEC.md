# CI/CD 仕様 (CICD_SPEC)

| 項目 | 内容 |
| --- | --- |
| ステータス | Draft |
| 最終更新日 | 2026-07-13 |
| 関連仕様 | [ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md), [AGENTCORE_SPEC.md](./AGENTCORE_SPEC.md) |

## 概要

`alexa-agent` の CI/CD パイプラインを定義する。GitHub Actions を用い、**OIDC による
AWS 認証(長期キーレス)**、**並列ジョブによる高速化**、**AgentCore Runtime(arm64
コンテナ)+ CDK デプロイ**を前提とする。現時点はアプリコード未実装のため、
**今すぐ動く検証(docs / diagram / actionlint)を実装しつつ、アプリ用ジョブは
コードが入り次第自動で有効化される形**で先行整備する。

## 背景・目的

- 仕様と構成図の整合を CI で継続的に守る(構成図のニアリアルタイム追従、[ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md))
- アプリ実装が始まったときに lint/typecheck/test/build → deploy の並列パイプラインが即使える土台を用意する
- クレデンシャルを GitHub に置かない(OIDC + 短期 STS)

## 仕様(確定事項)

### パイプライン全体

```mermaid
flowchart LR
    subgraph CI["CI (PR / push) — 並列"]
        docs[docs<br/>markdown/link]
        diagram[diagram<br/>図生成の健全性]
        actionlint[actionlint<br/>workflow 検証]
        lint[lint*]
        typecheck[typecheck*]
        test[test*]
        build[build (arm64)*]
    end
    subgraph CD["CD (main / 手動)"]
        deploy[cdk deploy<br/>OIDC]
    end
    docs & diagram & actionlint & lint & typecheck & test & build --> deploy
    classDef future fill:#eee,stroke:#999,stroke-dasharray:3;
    class lint,typecheck,test,build future;
```

`*` = アプリコード(`package.json`)が存在する場合のみ実行。未実装の現状ではスキップされる。

### CI ジョブ(`.github/workflows/ci.yml`)

すべて**並列実行**。相互依存はない。

| ジョブ | 内容 | 実行条件 |
| --- | --- | --- |
| `docs` | Markdown Lint + リンク切れチェック | 常時 |
| `diagram` | Graphviz/diagrams をセットアップし `docs/diagrams/*.py` を実行、図生成コードが壊れていないことを検証 | 常時 |
| `actionlint` | GitHub Actions ワークフローの静的検証 | 常時 |
| `lint` | ESLint | `package.json` 存在時 |
| `typecheck` | `tsc --noEmit` | `package.json` 存在時 |
| `test` | ユニットテスト | `package.json` 存在時 |
| `build` | TypeScript ビルド + コンテナイメージ(arm64)のビルド検証 | `package.json` 存在時 |

- TS 系ジョブは `if: ${{ hashFiles('package.json') != '' }}` でガードし、コード投入後に自動有効化する。
- モノレポ化した場合は各ジョブを**パッケージ matrix**(または Turborepo/nx の `--affected`)で並列化する。

### CD ジョブ(`.github/workflows/deploy.yml`)

- トリガー: `main` への push(アプリ/インフラ変更時)+ 手動(`workflow_dispatch`)。
- **OIDC 認証**: `permissions: { id-token: write, contents: read }` + `aws-actions/configure-aws-credentials`(`role-to-assume`)。長期アクセスキーは使わない。
- デプロイ本体: `npx cdk deploy`(`aws-cdk-lib/aws-bedrockagentcore` L2 で Runtime/Memory/Identity 等を構築)。arm64 コンテナは CDK の `fromAsset`(または事前 build ジョブ)でビルドし ECR へ。
- **ガード**: リポジトリ変数 `AWS_DEPLOY_ROLE_ARN` が未設定の間はデプロイジョブを**スキップ**(初期状態で失敗しないため)。OIDC ロール準備後に有効化する。

### 前提セットアップ(手動・一度きり)

CD を有効化するには以下が必要(未了のため Issue 化):

1. **GitHub OIDC プロバイダ**を AWS アカウントに作成(`token.actions.githubusercontent.com`)。
2. デプロイ用 **IAM ロール**を作成し、信頼ポリシーを当該リポジトリ/ブランチに限定。
3. リポジトリ変数 `AWS_DEPLOY_ROLE_ARN`・`AWS_REGION` を設定。
4. CDK bootstrap(`cdk bootstrap`)を対象アカウント/リージョンで実施。

### 並列化の方針

- CI の独立ジョブはすべて同時実行(依存を張らない)。
- deploy は全 CI ジョブの成功を `needs` で待ってから実行(品質ゲート)。
- ビルドが重くなったら arm64 セルフホストランナー or CodeBuild への委譲を検討。

## 未確定事項 (Open Questions)

- [ ] Runtime デプロイを CDK に寄せるか `@aws/agentcore deploy`(CodeBuild)に寄せるか([ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md) と連動)
- [ ] arm64 イメージビルドを GitHub ホストランナー(buildx/QEMU)/ arm64 ランナー / CodeBuild のどれで行うか
- [ ] 環境分離(dev/stg/prod)と GitHub Environments・承認フローの設計
- [ ] Alexa スキルパッケージのデプロイを `@alexa/ask-cdk`(CDK 一体)にするか `ask-cli` にするか
- [ ] 構成図の CI を「生成の健全性チェック」から「差分検出(未コミット検出)」に強化するか(PNG レンダリングの非決定性に注意)

## 変更履歴

| 日付 | 変更内容 |
| --- | --- |
| 2026-07-13 | 初版作成 |
