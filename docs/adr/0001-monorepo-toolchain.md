# ADR-0001: モノレポと開発ツール

- Status: Accepted
- Date: 2026-07-14
- Related: #7 #9 #10 #11 #17

## Context

AgentCoreエージェント、Alexa Lambda、CDK、共有コードを独立して検証しつつ、
単一PRで互換性を保つ必要がある。アプリコードはまだ存在しないため、先に共通の品質ゲートを用意する。

## Decision

- pnpm workspacesで `apps/*`、`infra/*`、`packages/*` を管理する。
- 内部依存は `workspace:` protocolを使用し、循環依存を禁止する。
- Turborepoで `lint`、`typecheck`、`test`、`build` の順序とキャッシュ対象を定義する。
- Node.js 22とpnpm 11を固定し、CIとローカルで同じコマンドを使う。
- trunk-based development、短命ブランチ、Conventional Commitsを採用する。
- 公開npmパッケージがない間はChangesetsを導入しない。

## Consequences

- アプリ追加時はpackage単位で責務と依存を分離できる。
- workspaceには共通scriptの実装が必要になる。
- pnpmのリリース直後24時間は `minimumReleaseAge` により依存解決対象外となる。

## Alternatives

- npm workspaces: 利用可能だが、workspace protocolと厳格な依存分離を優先して不採用。
- Changesetsの即時導入: 公開対象がなく運用コストだけが発生するため延期。

## References

- [pnpm Workspace](https://pnpm.io/workspaces)
- [Turborepo: Configuring tasks](https://turborepo.com/docs/crafting-your-repository/configuring-tasks)
