# ADR-0002: MVPのAgentCore Runtime Inbound認証

- Status: Accepted
- Date: 2026-07-14
- Related: #1 #6 #16

## Context

Alexa LambdaからAgentCore Runtimeを呼び出すMVPはAWS内のservice-to-service通信である。
RuntimeはIAM SigV4とOAuth JWTのどちらか一方をInbound認証に選択する。

## Decision

- MVPはIAM SigV4を使用する。
- Lambda実行ロールへ対象Runtimeに限定した `bedrock-agentcore:InvokeAgentRuntime` を付与する。
- AWS SDK for JavaScriptの `InvokeAgentRuntime` を使用する。
- Account Linking導入時もAlexaのエンドユーザーtokenをRuntime認証へ直接流用しない。
- ユーザー委任で外部サービスへ接続する段階で、JWT Runtimeの別versionまたはGatewayを再評価する。

## Consequences

- Cognito M2M、client secret、token cache、生HTTPS実装がMVPから不要になる。
- IAM principal単位でCloudTrailと権限境界を管理できる。
- エンドユーザー単位のRuntime認可が必要になった場合は追加設計が必要になる。

## Alternatives

- Cognito JWT: エンドユーザー認証には適するが、AWS SDKでRuntimeを呼べずMVPの実装と秘密情報管理が増えるため不採用。

## References

- [AgentCore Runtime security best practices](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-security-best-practices.html)
- [Invoke an AgentCore Runtime agent](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-invoke-agent.html)
