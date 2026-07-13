"""Amazon Bedrock AgentCore 全体像

docs/assets/agentcore_overview.png を生成する。
AgentCore Runtime を中心に、周辺サービス(Memory/Gateway/Identity/Observability/
Code Interpreter/Browser)と Bedrock 基盤モデルの関係を俯瞰する。
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import Cognito
from diagrams.onprem.client import Client
from diagrams.onprem.network import Internet

graph_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "15", "pad": "0.5", "splines": "spline"}
node_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "11"}
edge_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "10"}

with Diagram(
    "Amazon Bedrock AgentCore 全体像",
    filename="../assets/agentcore_overview",
    outformat="png",
    direction="LR",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    caller = Client("呼び出し元\n(Lambda / アプリ)")

    with Cluster("Amazon Bedrock AgentCore"):
        runtime = Bedrock("Runtime\n(エージェント実行)")

        with Cluster("記憶 / 認証"):
            memory = Bedrock("Memory\n(短期/長期記憶)")
            identity = Cognito("Identity\n(認証/Token Vault)")

        with Cluster("ツール"):
            gateway = Bedrock("Gateway\n(MCP ツール)")
            codeint = Bedrock("Code Interpreter\n(コード実行)")
            browser = Bedrock("Browser\n(Web 操作)")

        obs = Cloudwatch("Observability\n(OTEL→CloudWatch)")

    model = Bedrock("Bedrock 基盤モデル\n(Claude 等)")
    ecr = ECR("ECR\n(arm64 イメージ)")
    ext = Internet("外部 API / Web")

    caller >> Edge(label="InvokeAgentRuntime") >> runtime
    ecr >> Edge(style="dashed", label="コンテナ") >> runtime
    runtime >> Edge(label="推論") >> model
    runtime >> Edge(label="記憶") >> memory
    runtime >> Edge(label="認証委譲") >> identity
    runtime >> Edge(label="ツール呼出") >> gateway
    runtime >> codeint
    runtime >> browser
    runtime >> Edge(style="dotted", label="トレース") >> obs
    gateway >> Edge(style="dotted", label="外部連携") >> ext
    browser >> Edge(style="dotted") >> ext
