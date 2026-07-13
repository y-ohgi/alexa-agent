# インターフェース仕様 (API_SPEC)

| 項目 | 内容 |
| --- | --- |
| ステータス | Draft |
| 最終更新日 | 2026-07-13 |
| 関連仕様 | [OVERVIEW_SPEC.md](./OVERVIEW_SPEC.md), [ARCHITECTURE_SPEC.md](./ARCHITECTURE_SPEC.md), [AUTH_SPEC.md](./AUTH_SPEC.md) |

## 概要

Alexa スキルの対話モデル(Invocation Name / Intent / Slot)と、
スキルエンドポイント(Lambda)⇔ Bedrock AgentCore Runtime 間の呼び出しインターフェースを定義する。

## 背景・目的

- 自由対話を「Alexa の Intent モデル」に載せるための対話モデル設計を固める
- Lambda と AgentCore の間のペイロードを定義し、双方を独立して実装できるようにする

## 仕様(確定事項)

### 1. Alexa 対話モデル

#### Invocation Name

| 項目 | 値 |
| --- | --- |
| Invocation Name (ja-JP) | エージェンツ |
| 起動発話例 | 「アレクサ、**エージェンツ**」/「アレクサ、**エージェンツを開いて**」/「アレクサ、**エージェンツで**明日の予定を考えて」 |

#### Intent 一覧

| Intent | 種別 | 役割 |
| --- | --- | --- |
| `GeneralQueryIntent` | カスタム | 自由発話を受けるキャッチオール Intent。`AMAZON.SearchQuery` 型スロット `query` で発話全体を受け取り、エージェントに渡す |
| `AMAZON.FallbackIntent` | ビルトイン | どの Intent にもマッチしない発話。`GeneralQueryIntent` と同様にエージェントへ渡す方針 |
| `AMAZON.HelpIntent` | ビルトイン | 使い方の説明を返す(固定文言、エージェントは呼ばない) |
| `AMAZON.StopIntent` / `AMAZON.CancelIntent` | ビルトイン | セッション終了 |
| `AMAZON.NavigateHomeIntent` | ビルトイン | 必須のため定義のみ |

`GeneralQueryIntent` のサンプル発話(例):

```
{query} について教えて
{query} を調べて
{query}
```

> 補足: `AMAZON.SearchQuery` はサンプル発話にキャリアフレーズが必要という制約があるため、
> 実装時に発話パターンを調整する。素の `{query}` 単独が許容されない場合は
> Fallback 側で拾う設計とする。

#### 対話フロー

1. **起動(LaunchRequest)**: 「こんにちは。なんでも聞いてください」等の初回応答を返し、セッションを開いたままにする(`shouldEndSession: false`)
2. **発話(GeneralQueryIntent / FallbackIntent)**: 発話テキストをエージェントに渡し、応答を読み上げてセッション継続
3. **終了(StopIntent / CancelIntent / SessionEndedRequest)**: 終了の挨拶を返してセッションを閉じる
4. マルチターンの文脈は AgentCore 側のセッションで維持する(Lambda はステートレス)

### 2. Lambda ⇔ AgentCore Runtime インターフェース

呼び出しには AgentCore の `InvokeAgentRuntime` API を使用する。

#### 認証

- リクエストには Cognito から取得した JWT を `Authorization: Bearer <JWT>` として付与する
  (スコープ: `alexa-agent/invoke`)
- トークンの取得・キャッシュ・AgentCore Runtime 側の検証設定は
  [AUTH_SPEC.md](./AUTH_SPEC.md) を参照

#### リクエストペイロード(案)

```json
{
  "prompt": "明日の東京の天気はどうなりそう?",
  "locale": "ja-JP"
}
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `prompt` | string | ユーザー発話テキスト(`query` スロット値、または Fallback 時の生発話) |
| `locale` | string | Alexa リクエストの locale。応答言語の制御に使う |

- `runtimeSessionId` はペイロードではなく `InvokeAgentRuntime` のパラメータとして渡す
  (Alexa の `session.sessionId` から導出。ARCHITECTURE_SPEC のセッション設計を参照)

#### レスポンスペイロード(案)

```json
{
  "response": "明日の東京は晴れの予報が多いようです。",
  "endSession": false
}
```

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `response` | string | 読み上げるテキスト(プレーンテキスト。SSML 化は Lambda 側の責務) |
| `endSession` | boolean | エージェントが会話の終了を判断した場合 `true`(MVP では常に `false` でも可) |

#### エラー・タイムアウト時の応答

| ケース | Lambda の応答 |
| --- | --- |
| AgentCore 呼び出しがデッドライン(約 7 秒)超過 | 「うまく考えがまとまりませんでした。もう一度短く話しかけてください」+ セッション継続 |
| AgentCore がエラーを返す | 「いま応答できません。しばらくしてからもう一度試してください」+ セッション終了 |

### 3. 音声応答の制約

- 応答はプレーンテキストで受け取り、Lambda が SSML(`<speak>`)に整形する
- エージェントには**音声で聞きやすい短い応答**(目安: 2〜3 文)を生成させる(システムプロンプトで制御)
- Markdown・URL・コードブロック等、読み上げに不向きな表現は生成しない

## 未確定事項 (Open Questions)

- [ ] `AMAZON.SearchQuery` の発話パターン制約の実機確認(素の自由発話をどこまで拾えるか)
- [ ] 応答テキストの上限文字数(Alexa の outputSpeech 上限 8,000 文字に対する実運用上限)
- [ ] Progressive Response のつなぎ文言(固定 or ランダム)
- [ ] `endSession` の判断をエージェントに委ねるか、MVP では常にセッション継続とするか
- [ ] Phase 2 のツール定義フォーマット(AgentCore Gateway 導入時に別仕様書 `TOOLS_SPEC.md` を起こす)

## 変更履歴

| 日付 | 変更内容 |
| --- | --- |
| 2026-07-13 | 初版作成 |
| 2026-07-13 | InvokeAgentRuntime の認証(JWT Bearer)を追記、AUTH_SPEC を関連仕様に追加 |
