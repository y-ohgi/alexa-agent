# ADR-0005: Alexaスキルのデプロイ方式

- Status: Accepted
- Date: 2026-07-14
- Related: #6 #19

## Context

Alexaスキルmanifest・対話モデルと、Lambda・IAMなどAWS資源ではライフサイクルとAPIが異なる。
古いcommunity constructへ依存せず、公式ツールで再現可能にする必要がある。

## Decision

- Alexaスキルmanifest、対話モデル、dialog検証はASK CLIで管理する。
- Lambda、IAM、ログなどAWS資源は `infra/cdk` で管理する。
- CIはASK CLIのvalidateを実行し、環境へのdeployはGitHub Environment承認後に行う。
- Alexa認証情報はGitHub Environmentのsecretとして扱い、リポジトリへ保存しない。

## Consequences

- 各サービスの公式ツールと更新経路を利用できる。
- CDKとASK CLI間でLambda ARNなどの受け渡しが必要になる。
- ローカル・CI用のASK CLI認証手順を別途整備する必要がある。

## Alternatives

- `@alexa/ask-cdk`: 長期保守とCDK v2対応を確認できないため不採用。
- `Alexa::ASK::Skill`: 認証情報とモデル更新の運用がASK CLIより複雑になるため不採用。

## References

- [ASK CLI overview](https://developer.amazon.com/en-US/docs/alexa/smapi/quick-start-alexa-skills-kit-command-line-interface.html)
- [Alexa Progressive Response API](https://developer.amazon.com/en-US/docs/alexa/custom-skills/progressive-response-api-reference.html)
