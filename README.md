# alexa-agent

AlexaカスタムスキルからAmazon Bedrock AgentCore上のTypeScriptエージェントを呼び出し、
音声でマルチターン対話するプロジェクトです。現在は仕様策定と開発基盤の整備段階で、
アプリケーションコードはまだありません。

## ドキュメント

- [仕様書](./docs/specs/README.md)
- [技術調査](./docs/research/README.md)
- [構成図](./docs/diagrams/README.md)
- [Architecture Decision Records](./docs/adr/README.md)
- [開発参加ガイド](./CONTRIBUTING.md)

## 開発基盤

- Node.js 22 / pnpm 11
- pnpm workspaces / Turborepo
- GitHub Actions / Dependabot
- AgentCore CLI / AWS CDK / ASK CLI

ローカル検証は次のコマンドで実行します。

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm check
```

実装予定のworkspace構成とデプロイ責務は [ADR-0001](./docs/adr/0001-monorepo-toolchain.md) と
[ADR-0004](./docs/adr/0004-deployment-ownership.md) を参照してください。
