"""alexa-agent AWS 構成図 (MVP)

docs/specs/assets/architecture.png を生成する。
実行方法・更新運用は docs/diagrams/README.md を参照。
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.iot import IotAlexaEcho, IotAlexaSkill
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import Cognito, SecretsManager
from diagrams.onprem.client import User

graph_attr = {
    "fontname": "Noto Sans CJK JP",
    "fontsize": "14",
    "pad": "0.4",
    "splines": "spline",
}
node_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "11"}
edge_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "10"}

with Diagram(
    "alexa-agent MVP 構成図",
    filename="../specs/assets/architecture",
    outformat="png",
    direction="LR",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    user = User("ユーザー")
    echo = IotAlexaEcho("Alexa デバイス")

    with Cluster("Alexa Cloud"):
        skill = IotAlexaSkill("Alexa Skill\n(Invocation: エージェンツ)")

    with Cluster("AWS"):
        endpoint = Lambda("スキルエンドポイント\n(TypeScript)")

        with Cluster("認証 (AUTH_SPEC)"):
            cognito = Cognito("Cognito User Pool\n(M2M / JWT 発行)")
            secrets = SecretsManager("Secrets Manager\n(クライアントシークレット)")

        with Cluster("Bedrock AgentCore"):
            runtime = Bedrock("AgentCore Runtime\n(Mastra Agent)")

        model = Bedrock("Bedrock 基盤モデル\n(Claude Haiku 4.5)")

        with Cluster("将来拡張 (Phase 2/3)", graph_attr={"style": "dashed"}):
            gateway = Bedrock("AgentCore Gateway\n(ツール連携)")
            memory = Bedrock("AgentCore Memory\n(記憶・パーソナライズ)")

    user >> Edge(label="「Alexa、エージェンツ」") >> echo >> skill
    skill >> Edge(label="IntentRequest\n(署名 + Skill ID 検証)") >> endpoint
    endpoint >> Edge(label="client_credentials\n→ JWT") >> cognito
    endpoint >> Edge(style="dashed", label="シークレット取得") >> secrets
    endpoint >> Edge(label="InvokeAgentRuntime\n(Bearer JWT)") >> runtime
    runtime >> Edge(label="推論") >> model

    runtime >> Edge(style="dotted", label="Phase 2") >> gateway
    runtime >> Edge(style="dotted", label="Phase 3") >> memory
