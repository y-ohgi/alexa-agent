# 構成図 (diagram-as-code)

AWS アイコンを使用した構成図を [mingrammer/diagrams](https://diagrams.mingrammer.com/) で
コードから生成します。生成物は `docs/specs/assets/` にコミットし、
[ARCHITECTURE_SPEC.md](../specs/ARCHITECTURE_SPEC.md) から参照します。

## ファイル

| ファイル | 内容 |
| --- | --- |
| `architecture.py` | MVP 全体構成図の定義 → `docs/specs/assets/architecture.png` を生成 |

## 生成手順

```bash
# 依存: Python 3.9+ / Graphviz / 日本語フォント
sudo apt-get install -y graphviz fonts-noto-cjk   # macOS: brew install graphviz
pip install diagrams

cd docs/diagrams
python3 architecture.py
```

## 運用ルール

- **構成を変更したら、同じ PR 内で `architecture.py` を修正し PNG を再生成してコミットする**
  (構成図はニアリアルタイム=デプロイ単位で実構成に追従させる)
- アイコンについて: AgentCore(Runtime / Gateway / Memory)は専用アイコンが
  `diagrams` に未収録のため、暫定で Bedrock アイコン + ラベルで表現している。
  公式アイコン追加後に差し替える

## 将来の自動化(予定)

CDK デプロイと同じ CI パイプラインに図の再生成ジョブを追加し、
デプロイ成功時に PNG を自動更新・コミットすることで手動運用を廃止する。
(検討メモ: CDK 構成から図を自動導出する `cdk-dia` への移行も選択肢)
