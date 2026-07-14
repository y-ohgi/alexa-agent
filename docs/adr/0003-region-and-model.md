# ADR-0003: AWSリージョンと初期モデル

- Status: Accepted
- Date: 2026-07-14
- Related: #2 #6 #15 #22

## Context

主な利用者とAlexa Far East endpointに近いリージョンを選び、8秒の応答制約を満たす必要がある。
モデル品質、レイテンシ、費用は実測前のため固定しすぎない。

## Decision

- MVPのAWSリージョンは `ap-northeast-1` とする。
- 初期モデルはClaude Haiku 4.5のJP cross-region inference profile
  `jp.anthropic.claude-haiku-4-5-20251001-v1:0` とする。
- fallback候補はAmazon Nova 2 LiteのJP profile
  `jp.amazon.nova-2-lite-v1:0` とする。
- モデルIDを設定として注入し、コードへ埋め込まない。
- #18と#22の実測でprimary/fallbackを最終確定し、MVPでは無条件の自動切り替えを行わない。
- データを東京リージョン内だけに限定する要件が生じた場合はIn-Region endpointを再評価する。

## Consequences

- 東京と大阪のJP geography内で推論がルーティングされ、単一リージョン障害とquotaの影響を緩和できる。
- 東京のみのデータレジデンシーは保証しない。
- モデル更新時はgolden evalとレイテンシ測定が必要になる。

## Alternatives

- Global inference: 可用性は高いが、MVPでは地理的な処理範囲をJPに限定するため不採用。
- In-Region model ID: 東京内処理が必要になるまでは、可用性を優先して延期。
- Nova 2 Liteを初期primaryにする案: 日本語音声品質の実測前なのでfallback候補に留める。

## References

- [Claude Haiku 4.5 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html)
- [Amazon Nova 2 Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html)
