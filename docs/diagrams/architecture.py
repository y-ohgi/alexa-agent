"""alexa-agent AWS 構成図 (MVP)

docs/specs/assets/architecture.png を生成する。
MVP は AgentCore Runtime / Identity(Inbound)/ Memory(短期)/ Observability を使用。
実行方法・更新運用は docs/diagrams/README.md を参照。
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR, Lambda
from diagrams.aws.iot import IotAlexaEcho, IotAlexaSkill
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import IAMRole
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
        endpoint = Lambda("Lambda アダプタ\n(TypeScript)")

        with Cluster("認証 (AUTH_SPEC)"):
            role = IAMRole("Lambda 実行ロール\n(IAM SigV4)")

        with Cluster("Bedrock AgentCore"):
            runtime = Bedrock("AgentCore Runtime\n(Mastra / HTTP :8080)")
            memory = Bedrock("AgentCore Memory\n(短期記憶 / events)")

        ecr = ECR("ECR\n(arm64 イメージ)")
        model = Bedrock("Bedrock 基盤モデル\n(Claude Haiku 4.5)")
        cw = Cloudwatch("CloudWatch\n(Observability / OTEL)")

    user >> Edge(label="「Alexa、エージェンツ」") >> echo >> skill
    skill >> Edge(label="IntentRequest\n(署名 + Skill ID 検証)") >> endpoint
    role >> Edge(style="dashed", label="最小権限") >> endpoint
    endpoint >> Edge(label="InvokeAgentRuntime\n(AWS SDK + SigV4)") >> runtime
    runtime >> Edge(label="推論") >> model
    runtime >> Edge(label="CreateEvent / ListEvents") >> memory
    ecr >> Edge(style="dashed", label="イメージ") >> runtime
    runtime >> Edge(style="dotted", label="トレース/メトリクス") >> cw
