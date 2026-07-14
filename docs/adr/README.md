# Architecture Decision Records

横断的で長期に影響する設計判断を記録する。

## 運用

- ファイル名は `NNNN-short-title.md` とする。
- Statusは `Proposed`、`Accepted`、`Superseded`、`Deprecated` のいずれかとする。
- 決定を変更するときは既存ADRを書き換えず、新しいADRから置き換え対象を参照する。
- PRには関連Issue、検討した選択肢、検証可能な結果を含める。

## 一覧

- [ADR-0001: モノレポと開発ツール](./0001-monorepo-toolchain.md)
- [ADR-0002: MVPのAgentCore Runtime Inbound認証](./0002-runtime-inbound-auth.md)
- [ADR-0003: AWSリージョンと初期モデル](./0003-region-and-model.md)
- [ADR-0004: デプロイ手段の責務分離](./0004-deployment-ownership.md)
- [ADR-0005: Alexaスキルのデプロイ方式](./0005-alexa-skill-deployment.md)

新規ADRは [_TEMPLATE.md](./_TEMPLATE.md) を複製して作成する。
