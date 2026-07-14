# 技術調査 (Research)

`alexa-agent` で使用する技術の調査資料を置くディレクトリです。
仕様書(`docs/specs/`)が「何をどう作るか(決定)」なのに対し、こちらは
「その技術は何ができるか(理解・根拠)」をまとめる**調査スナップショット**です。

画像は [`docs/assets/`](../assets/) に配置します(diagram-as-code の生成物は
[`docs/diagrams/`](../diagrams/) のスクリプトから生成)。

## 調査資料一覧

| ファイル | 内容 | 図 |
| --- | --- | --- |
| [ALEXA.md](./ALEXA.md) | Amazon Alexa カスタムスキル開発(構成/ライフサイクル/ASK SDK/8秒制約/ツール) | Mermaid |
| [AGENTCORE.md](./AGENTCORE.md) | Amazon Bedrock AgentCore 概要と各機能(Runtime/Memory/Gateway/Identity/Observability/Code Interpreter/Browser) | アーキ画像([docs/assets](../assets/)) |
| [BEDROCK_MODELS.md](./BEDROCK_MODELS.md) | 音声対話向けモデル候補と実測ゲート | なし |
| [COST.md](./COST.md) | MVPコストモデルと予算・runaway防止策 | なし |
| [DEVELOPMENT_FOUNDATION.md](./DEVELOPMENT_FOUNDATION.md) | モノレポ、認証、デプロイ、モデル、Alexa制約の開発基盤調査 | なし |
| [MASTRA.md](./MASTRA.md) | MastraとAgentCore Runtimeの公式統合方式 | なし |

## 今後の調査予定(必要に応じて追加)

- **CDK_AGENTCORE.md** — AgentCore の CDK/CloudFormation/Terraform 対応と construct の成熟度(L1/L2、`aws-bedrockagentcore` の安定版 vs alpha の食い違いを一次情報で確定)。

## 運用メモ

- 調査は時点情報。各資料の冒頭に調査時点を明記し、実装着手時に一次情報(AWS 公式等)で再確認する。
- 図を更新したら生成スクリプト([`docs/diagrams/`](../diagrams/))も同一 PR で更新する。
