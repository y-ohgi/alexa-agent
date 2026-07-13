# ADR-0004: デプロイ手段の責務分離

- Status: Accepted
- Date: 2026-07-14
- Related: #3 #6 #13 #20

## Context

AgentCore CLIはTypeScript、CodeZip、ローカル開発、検証、CDKベースのplan/deployを公式に扱う。
一方、Alexa LambdaなどAgentCore外の資源も必要になる。同一資源の二重管理を避ける。

## Decision

- Runtime、Memory、EvaluatorなどAgentCore CLIが扱う資源は `agentcore/agentcore.json` を正とする。
- `agentcore validate` と `agentcore deploy --plan` をCIの事前検証に使用する。
- Alexa Lambda、IAM連携、ログ、アラームなど周辺資源は `infra/cdk` で管理する。
- AgentCore L2 constructを独自CDKから使うのは、CLIで表現できない要件が確認された場合に限定する。
- 同じCloudFormationリソースをAgentCore CLIと `infra/cdk` から管理しない。

## Consequences

- 公式CLIの更新とTypeScript向けパッケージングを利用できる。
- デプロイスタックは複数になるため、出力値とデプロイ順序を明示する必要がある。
- CLIで不足する要件が出た場合はADRを更新して所有権を移す。

## Alternatives

- 全資源を独自CDKで管理: 一元化できるが、CLIのdev、validate、CodeZip packagingと重複するため不採用。
- 全資源をAgentCore CLIで管理: Alexa固有資源を管理できないため不採用。

## References

- [AgentCore CLI TypeScript guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli-typescript.html)
- [AWS CDK AgentCore Runtime construct](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_bedrockagentcore.Runtime.html)
