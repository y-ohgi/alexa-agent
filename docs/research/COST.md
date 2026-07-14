# MVPコストモデルとガードレール

- 調査日: 2026-07-14
- 関連Issue: #15 #23

## 結論

- MVPの主要変動費はBedrock model、AgentCore Runtime、Memory、CloudWatchである。
- Runtimeはactive CPUとmemoryに対する従量課金で、I/O wait中のCPUは課金対象外になる。
- 短期Memoryは1,000 new eventsあたりUSD 0.25であり、2 events/turnならmodel以外で無視できない。
- model単価は設定や文書へ固定せず、利用開始時のAWS公式価格を計算sheetへ保存する。
- devでは月次USD 10、stgではUSD 25を初期budget目安とし、prodは実測後に決定する。

## 単価スナップショット

AgentCore公式価格ページで確認した代表単価は次のとおり。税、region差、CloudWatch、data transfer、
Bedrock model利用料は別途考慮する。

- Runtime CPU: USD 0.0895 / vCPU-hour
- Runtime memory: USD 0.00945 / GB-hour
- Short-term Memory: USD 0.25 / 1,000 new events
- Long-term Memory built-in storage: USD 0.75 / 1,000 records-month
- Long-term Memory retrieval: USD 0.50 / 1,000 calls
- Observability: CloudWatch料金に従う

## 計算式

1 sessionあたりの概算を次で計算する。

```text
runtime_cpu = active_cpu_seconds * vCPU * 0.0895 / 3600
runtime_memory = session_seconds * memory_GB * 0.00945 / 3600
short_term_memory = new_events * 0.25 / 1000
model = input_tokens * input_price_per_million / 1_000_000
      + output_tokens * output_price_per_million / 1_000_000
total = runtime_cpu + runtime_memory + short_term_memory + model + cloudwatch + lambda
```

例として5秒のsession、active CPU 2秒、1 vCPU、2 GB、Memory 2 eventsの場合、
model・CloudWatch・Lambdaを除く概算は次のとおり。

- Runtime CPU: 約USD 0.000050
- Runtime memory: 約USD 0.000026
- Short-term Memory: USD 0.000500
- 合計: 約USD 0.000576 / session
- 10,000 sessions: 約USD 5.76 + model・CloudWatch・Lambda

この仮定ではMemoryがRuntimeより大きいため、MVPでMemoryを使う価値をsession内文脈だけの場合と比較する。

## 利用シナリオ

- local: AWSを使わずfixtureとmockを基本とする
- dev: 開発者の手動試験、月1,000 sessions以下
- stg: evalとAlexa実機試験、実行回数をCIで制限
- prod: DAU、turn/user、token/turn、timeout率の実測から予算を再計算

## ガードレール

- AWS Budgetsで50%、80%、100%通知を設定する
- Cost Anomaly Detectionをproject/environment tag単位で有効化する
- 必須tagを `project=alexa-agent`、`environment`、`component` とする
- 1 requestの出力token、tool call回数、agent step、wall-clock deadlineを制限する
- online evalとload testには日次実行数上限を設ける
- CloudWatch log retentionをdev 7日、stg 30日から開始する
- session ID、user ID、prompt本文を高カーディナリティmetric dimensionへ使用しない
- 異常時はmodel呼び出しを止め、固定fallback応答へ切り替えられるfeature flagを用意する

AWS Budgetは支出を自動停止しないため、通知だけをrunaway防止策としない。実装側のdeadline、回数上限、
feature flagと組み合わせる。金額、通知先、prod budgetはAWS account ownerの承認後に設定する。

## 一次情報

- [Amazon Bedrock AgentCore pricing](https://aws.amazon.com/bedrock/agentcore/pricing/)
- [Amazon Bedrock pricing](https://aws.amazon.com/bedrock/pricing/)
- [AgentCore cost analysis guidance](https://docs.aws.amazon.com/solutions/cost-analysis-and-optimization-with-amazon-bedrock-agentcore-on-aws/)
