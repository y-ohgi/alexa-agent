# 仕様書 (Specs)

このディレクトリでは `alexa-agent` の仕様書を管理します。

## 仕様書一覧

| ファイル | 内容 | ステータス |
| --- | --- | --- |
| [OVERVIEW_SPEC.md](./OVERVIEW_SPEC.md) | プロダクト概要・ユースケース・スコープ | Draft |
| [AGENTCORE_SPEC.md](./AGENTCORE_SPEC.md) | AgentCore 各機能の用途・採用フェーズ | Draft |
| [ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md) | システム構成・コンポーネント責務・設計制約 | Draft |
| [API_SPEC.md](./API_SPEC.md) | Alexa 対話モデル・コンポーネント間インターフェース | Draft |
| [AUTH_SPEC.md](./AUTH_SPEC.md) | 認証認可(ASK 検証・AgentCore Inbound/Outbound Auth) | Draft |
| [CICD_SPEC.md](./CICD_SPEC.md) | CI/CD パイプライン(GitHub Actions・OIDC・並列ジョブ) | Draft |

## 命名規則

- 仕様書のファイル名は `<TOPIC>_SPEC.md` とする(UPPER_SNAKE_CASE + suffix `_SPEC`)
  - 例: `OVERVIEW_SPEC.md`, `ARCHITECTURE_SPEC.md`, `MEMORY_SPEC.md`
- 仕様書以外の補助ファイルには `_SPEC` を付けない(例: `_TEMPLATE.md`)

## ステータス管理

各仕様書は冒頭のメタ情報表でステータスを管理します。

| ステータス | 意味 |
| --- | --- |
| `Draft` | 執筆中。未確定事項(Open Questions)が残っている |
| `Review` | 内容が揃い、レビュー・合意待ち |
| `Approved` | 合意済み。実装の根拠として参照できる |

- 仕様の議論・決定は各仕様書の「未確定事項 (Open Questions)」セクションを起点に行う
- 決定した事項は「仕様(確定事項)」へ移し、変更履歴に記録する
- `Approved` 後に仕様を変更する場合はステータスを `Review` に戻す

## 新しい仕様書の作り方

1. [`_TEMPLATE.md`](./_TEMPLATE.md) をコピーして `<TOPIC>_SPEC.md` を作成する
2. メタ情報(ステータス・更新日・関連仕様)を記入する
3. この README の仕様書一覧に追記する
