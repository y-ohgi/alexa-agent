# 音声対話向けBedrockモデル調査

- 調査日: 2026-07-14
- リージョン: `ap-northeast-1`
- 関連Issue: #2 #18 #22

## 結論

- primary候補はClaude Haiku 4.5のJP inference profileとする。
- fallback候補はAmazon Nova 2 LiteのJP inference profileとする。
- model IDは環境設定で切り替え、アプリケーションコードへ埋め込まない。
- 最終選定は同一golden datasetによる日本語品質、p95 latency、costの実測後に行う。

## 候補

### Claude Haiku 4.5

- Model ID: `anthropic.claude-haiku-4-5-20251001-v1:0`
- JP profile: `jp.anthropic.claude-haiku-4-5-20251001-v1:0`
- 東京から東京・大阪へgeo routingされる。
- response streaming、tool use、Guardrails等を利用できる。
- 音声対話で重要な自然な日本語、短文指示追従、tool calling品質の基準モデルとする。

### Amazon Nova 2 Lite

- Model ID: `amazon.nova-2-lite-v1:0`
- JP profile: `jp.amazon.nova-2-lite-v1:0`
- 東京から東京・大阪へgeo routingされる。
- response streaming、Guardrails、client-side tool calling、prompt cachingを利用できる。
- 東京ではIn-Region endpointを提供せず、JPまたはGlobal profileを使用する。
- costとlatencyを優先するfallback候補とする。

旧Nova Micro/Liteではなく、activeなNova 2 Liteを比較対象とする。text-onlyの音声応答生成でも
multimodal機能は必須ではないため、品質・latency・costがHaikuを上回る場合のみprimaryへ昇格する。

## Golden dataset

最低30件を固定し、同じprompt、temperature、出力上限で比較する。

- 日本語の日常会話と曖昧な依頼
- 1〜3turnの文脈参照
- Alexaで読み上げやすい2〜3文への圧縮
- Markdown、URL、code blockを出さない制約
- toolを使う／使わない判断
- 不明時に推測せず確認する応答

評価項目はtask success、日本語自然さ、簡潔さ、禁止表現、TTFT、end-to-end latency、入出力token、
1turn costとする。自動評価だけで確定せず、音声での人手確認を含める。

## 採用ゲート

- Alexa end-to-end p95が7秒以内
- timeout率が1%未満
- golden datasetの重大失敗が0件
- 平均出力が音声向け上限内
- model access、quota、JP profileが対象AWS accountで利用可能

価格とquotaは変更されるため、実測日と参照単価を結果へ保存する。profile障害時に自動で別modelへ
切り替えると応答品質が変わるため、MVPでは無条件の自動fallbackを行わず、明示的なfeature flagで切り替える。

## 一次情報

- [Claude Haiku 4.5 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-haiku-4-5.html)
- [Amazon Nova 2 Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html)
- [Bedrock regional availability](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html)
- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
