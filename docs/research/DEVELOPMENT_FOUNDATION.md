# 開発基盤調査

- 調査日: 2026-07-14
- 対象: モノレポ、AgentCoreデプロイ、MVP認証、モデル、Alexa応答制約

## 結論

- pnpm workspacesとTurborepoを採用し、packageごとの品質タスクをルートから統一実行する。
- Node.js 22、pnpm 11を固定し、依存公開から24時間待つ `minimumReleaseAge` を設定する。
- AgentCore Runtimeは公式AgentCore CLI、Alexa Lambdaなどの周辺AWS資源はCDKで管理する。
- MVPのRuntime Inbound認証はIAM SigV4を採用する。
- リージョンは東京、初期モデルはClaude Haiku 4.5のJP inference profileとする。
- Alexaの最終応答はProgressive Responseを含めて8秒以内であり、実測スパイクを実装前のゲートとする。

詳細な決定と代替案は [ADR一覧](../adr/README.md) を参照する。

## 調査結果

### モノレポ

pnpmは `pnpm-workspace.yaml` をworkspaceの正とし、`workspace:` protocolでローカルpackage以外への
誤解決を防げる。共有lockfileと循環依存禁止を使用する。Turborepoはpackage間のtask依存と成果物を
宣言できるため、アプリが増えてもルートの `pnpm check` を維持できる。

Changesetsはpnpmが案内するrelease workflowの選択肢だが、現時点では公開packageがない。
公開packageの追加時に導入を再評価し、アプリのAWSデプロイとは分離する。

### AgentCoreデプロイ

現行のAgentCore CLIはTypeScriptを公式サポートし、`agentcore dev`、`validate`、
`deploy --plan`、`deploy` を提供する。TypeScriptのコンパイルとCodeZip packaging、CDKによる
Runtime作成もCLIが担う。Mastra固有のartifact形式は#21で検証するが、Runtime資源を独自CDKと
二重管理しない原則は先に確定できる。

### 認証

AWS公式security best practicesは、AWS内のservice-to-service呼び出しにIAM SigV4、
エンドユーザーがIdPで直接認証する場合にJWTを推奨する。Alexa LambdaからRuntimeを呼ぶMVPは
前者に該当する。JWTではAWS SDKの `InvokeAgentRuntime` を使用できないため、Cognito M2Mは
MVPの遅延、秘密情報、実装量を増やす。

### リージョンとモデル

Claude Haiku 4.5のモデルカードでは、東京からJP inference profileを使用でき、東京・大阪へ
ルーティングされる。初期値は `jp.anthropic.claude-haiku-4-5-20251001-v1:0` とする。
品質、p95遅延、費用、Nova系fallbackは#18、#22、#23で実測する。

### Alexaの8秒制約

Alexa Progressive Response APIは処理中の音声を返せるが、最終応答までの8秒制約を延長しない。
Lambda内部のデッドラインを7秒にし、フォールバック時間を確保する。実機のend-to-end測定は#18で行う。

## 一次情報

- [pnpm Workspace](https://pnpm.io/workspaces)
- [pnpm Settings](https://pnpm.io/settings)
- [Turborepo: Configuring tasks](https://turborepo.com/docs/crafting-your-repository/configuring-tasks)
- [AgentCore CLI TypeScript guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli-typescript.html)
- [AgentCore Runtime security best practices](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-security-best-practices.html)
- [Invoke an AgentCore Runtime agent](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-invoke-agent.html)
- [Claude Haiku 4.5 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html)
- [Alexa Progressive Response API](https://developer.amazon.com/en-US/docs/alexa/custom-skills/progressive-response-api-reference.html)
