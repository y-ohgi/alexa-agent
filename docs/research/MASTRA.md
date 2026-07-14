# MastraとAgentCore Runtime統合調査

- 調査日: 2026-07-14
- 関連Issue: #21

## 結論

- MastraはAgentCore CLIのBYO TypeScript agentとして登録し、`build: Container`でデプロイする。
- `bedrock-agentcore/runtime`の `BedrockAgentCoreApp` でHTTP契約を実装する。
- Mastra既定のfile-based storageとobservability設定は無効化する。
- Runtime execution roleの資格情報をAWS SDK standard provider chainから取得する。
- Alexa向けMVPは非streaming JSON応答を使用し、AgentCore内部のstreamingは後続検証とする。

## 公式統合方式

Mastra公式ガイドはAgentCore CLIで空のprojectを作成し、MastraをBYO TypeScript agentとして
`app/MastraAgent`へ配置する。CLI登録時の主要設定は次のとおり。

```text
type: byo
build: Container
language: TypeScript
code-location: app/MastraAgent
```

CLIはCodeBuildでarm64 imageをbuildし、ECRへpushしてRuntimeとDEFAULT endpointを作成する。
ローカルのDocker daemonは `agentcore deploy` には不要だが、`agentcore dev` には必要になる。

## Runtime handler

`BedrockAgentCoreApp` の `invocationHandler.process` でpayloadとsession contextを受け取り、
`mastra.getAgentById()` で対象agentを取得して `agent.generate()` を呼ぶ。AgentCoreの
`context.sessionId` はMastraの `runId` へ渡し、Alexa sessionとの相関に使用する。

Runtime HTTP契約は `0.0.0.0:8080` の `POST /invocations` と `GET /ping` である。
`/invocations` はJSONまたはSSEを返せるが、Alexaは最終応答を一括で必要とするため、MVPでは
短いJSON responseを返す。streamingの利用はLambda内で全chunkを集約する場合に限定する。

## Storageとfilesystem

AgentCore Runtime containerはnon-rootでapplication directoryがread-onlyになる。
Mastra既定の `LibSQLStore` は `./mastra.db` を開けずstartupに失敗するため、MVPでは
file-based storageを設定しない。会話状態はAgentCore sessionとMemoryへ明示的に保存する。

永続storageが必要になった場合は、DynamoDB等の外部storeを選定し、container filesystemへ
依存しない。生成物や一時fileもapplication directoryへ書き込まない。

## Observability

Container起動時に `@opentelemetry/auto-instrumentations-node/register` をpreloadする。
Mastra側の既定observabilityを重複して有効化せず、AgentCore Observabilityのtraceを正とする。
Alexa request ID、AgentCore session ID、Mastra run IDをstructured logへ記録して相関する。

## 実装時の検証項目

- [ ] arm64 imageがnon-rootで起動する
- [ ] read-only application directoryで `/ping` と `/invocations` が成功する
- [ ] `context.sessionId` がMastra `runId` とtraceへ伝播する
- [ ] SigV4で呼び出した応答が7秒のLambda deadline内に完了する
- [ ] error、timeout、empty responseをAlexa向けfallbackへ変換できる
- [ ] OpenTelemetryの二重計装や重複spanがない

## 一次情報

- [Mastra: Deploy to Amazon Bedrock AgentCore](https://mastra.ai/guides/deployment/aws-bedrock-agentcore)
- [AgentCore HTTP protocol contract](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-http-protocol-contract.html)
- [AgentCore CLI TypeScript guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli-typescript.html)
