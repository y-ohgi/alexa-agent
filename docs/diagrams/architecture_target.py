"""alexa-agent AWS ターゲット構成図(AgentCore フル活用)

docs/specs/assets/architecture_target.png を生成する。
MVP〜Phase 3 で採用する AgentCore コンポーネントを一枚に俯瞰する。
フェーズ別の採用方針は docs/specs/AGENTCORE_SPEC.md を参照。
実行方法・更新運用は docs/diagrams/README.md を参照。
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR, Lambda
from diagrams.aws.iot import IotAlexaEcho, IotAlexaSkill
from diagrams.aws.management import Cloudwatch
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import Cognito, IAMRole, SecretsManager
from diagrams.onprem.client import User

graph_attr = {
    "fontname": "Noto Sans CJK JP",
    "fontsize": "14",
    "pad": "0.5",
    "splines": "spline",
    "nodesep": "0.5",
    "ranksep": "1.0",
}
node_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "11"}
edge_attr = {"fontname": "Noto Sans CJK JP", "fontsize": "10"}

with Diagram(
    "alexa-agent ターゲット構成図 (AgentCore フル活用)",
    filename="../specs/assets/architecture_target",
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

        with Cluster("認証 / Identity (AUTH_SPEC)"):
            cognito = Cognito("Cognito\n(JWT / Account Linking)")
            secrets = SecretsManager("Secrets Manager")
            identity = Bedrock("AgentCore Identity\n(Workload ID / Token Vault)")

        with Cluster("Bedrock AgentCore"):
            runtime = Bedrock("AgentCore Runtime\n(Mastra / HTTP :8080)")

            with Cluster("MVP"):
                memory_st = Bedrock("Memory 短期\n(events)")

            with Cluster("Phase 2"):
                gateway = Bedrock("Gateway\n(MCP ツール)")
                codeint = Bedrock("Code Interpreter\n(サンドボックス)")

            with Cluster("Phase 3"):
                memory_lt = Bedrock("Memory 長期\n(要約/嗜好/事実)")
                browser = Bedrock("Browser Tool\n(Headless Chrome)")

        ecr = ECR("ECR (arm64)")
        model = Bedrock("Bedrock モデル\n(Claude Haiku 4.5)")
        cw = Cloudwatch("CloudWatch\n(Observability)")

    with Cluster("外部サービス (Phase 2/3)"):
        ext = IAMRole("外部 API / SaaS\n(天気・カレンダー等)")

    # 主経路
    user >> Edge(label="「Alexa、エージェンツ」") >> echo >> skill
    skill >> Edge(label="IntentRequest") >> endpoint
    endpoint >> Edge(label="JWT 取得") >> cognito
    endpoint >> Edge(style="dashed") >> secrets
    endpoint >> Edge(label="InvokeAgentRuntime\n(HTTPS + JWT)") >> runtime
    runtime >> Edge(label="推論") >> model

    # AgentCore 機能連携
    runtime >> Edge(label="短期記憶") >> memory_st
    runtime >> Edge(style="dotted", label="Phase 2") >> gateway
    runtime >> Edge(style="dotted", label="Phase 2") >> codeint
    runtime >> Edge(style="dotted", label="Phase 3") >> memory_lt
    runtime >> Edge(style="dotted", label="Phase 3") >> browser
    runtime >> Edge(style="dotted", label="トレース") >> cw

    # Identity / 外部連携
    runtime >> Edge(style="dashed", label="Workload ID") >> identity
    gateway >> Edge(style="dotted", label="Credential Provider") >> identity
    gateway >> Edge(style="dotted", label="ツール呼び出し") >> ext
    ecr >> Edge(style="dashed", label="イメージ") >> runtime
