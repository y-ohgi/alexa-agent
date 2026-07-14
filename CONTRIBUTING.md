# Contributing

## 前提

- Node.js 22 (`.nvmrc`)
- Corepack
- pnpm 11 (`package.json` の `packageManager`)

秘密情報を含む `.env`、認証情報、Cookie、ログをリポジトリへ追加しない。

## セットアップ

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm check
```

## 開発フロー

1. `main` から短命なブランチを作成する。
2. Conventional Commits形式で変更を記録する。
3. `pnpm check` を実行してからPRを作成する。
4. 設計判断を伴う場合は `docs/adr/` を追加または更新する。

アプリ実装後は、各workspaceに `lint`、`typecheck`、`test`、`build` を定義する。
ルートのTurborepoタスクが全workspaceへ同じ品質ゲートを適用する。

## ディレクトリ方針

- `apps/agent`: MastraとAgentCore Runtimeのエージェント
- `apps/alexa-adapter`: AlexaからRuntimeを呼び出すLambda
- `infra/cdk`: Alexa Lambdaなど周辺AWS資源のCDK
- `packages/*`: 複数アプリで共有する設定、型、テスト支援
- `docs/adr`: 横断的な設計判断

内部パッケージは `workspace:*` で参照し、循環依存を作らない。

## デプロイ責務

- AgentCore RuntimeとCLI対応リソース: `agentcore/agentcore.json` とAgentCore CLI
- Alexa Lambdaなど周辺AWS資源: `infra/cdk`
- Alexaスキルmanifest・対話モデル: ASK CLI

同じCloudFormationリソースを複数のデプロイ手段で管理しない。
AWSへのデプロイにはGitHub Environmentの承認とOIDCロールを使用する。

## リリース

現時点では公開npmパッケージがないためChangesetsは使用しない。
外部公開パッケージが追加された時点で、独立バージョニングとCHANGELOG生成の要否を再評価する。
