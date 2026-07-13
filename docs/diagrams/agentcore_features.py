"""Amazon Bedrock AgentCore 各機能のアーキテクチャ図

docs/assets/ に機能ごとの PNG を生成する:
  - agentcore_runtime.png
  - agentcore_memory.png
  - agentcore_gateway.png
  - agentcore_identity.png
  - agentcore_observability.png
"""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECR, Fargate, Lambda
from diagrams.aws.management import Cloudtrail, Cloudwatch, CloudwatchLogs
from diagrams.aws.ml import Bedrock
from diagrams.aws.security import Cognito, IAMRole, KMS, SecretsManager
from diagrams.aws.storage import S3
from diagrams.onprem.client import Client
from diagrams.onprem.network import Internet

GRAPH = {"fontname": "Noto Sans CJK JP", "fontsize": "15", "pad": "0.4", "splines": "spline"}
NODE = {"fontname": "Noto Sans CJK JP", "fontsize": "11"}
EDGE = {"fontname": "Noto Sans CJK JP", "fontsize": "10"}


def diagram(title, filename, direction="LR"):
    return Diagram(
        title, filename=filename, outformat="png", direction=direction,
        show=False, graph_attr=GRAPH, node_attr=NODE, edge_attr=EDGE,
    )


# 1. Runtime -----------------------------------------------------------------
with diagram("AgentCore Runtime", "../assets/agentcore_runtime"):
    caller = Client("呼び出し元")
    ecr = ECR("ECR\n(arm64 イメージ)")
    with Cluster("AgentCore Runtime"):
        with Cluster("Endpoint (DEFAULT / カスタム)"):
            with Cluster("セッションごとの microVM\n(CPU/メモリ/FS 隔離)"):
                agent = Fargate("エージェント コンテナ\nHTTP :8080\n/invocations /ping")
    model = Bedrock("Bedrock 基盤モデル")
    caller >> Edge(label="InvokeAgentRuntime\n(runtimeSessionId, payload≤100MB)") >> agent
    ecr >> Edge(style="dashed", label="デプロイ") >> agent
    agent >> Edge(label="推論 (SSE)") >> model


# 2. Memory ------------------------------------------------------------------
with diagram("AgentCore Memory", "../assets/agentcore_memory"):
    agent = Bedrock("エージェント")
    with Cluster("AgentCore Memory"):
        with Cluster("短期記憶 (MVP)"):
            events = Bedrock("events\n(会話ターン)\nactorId / sessionId")
        with Cluster("長期記憶 (Phase 3)"):
            records = Bedrock("memory records\n(Semantic / Summary /\nUserPreference)")
    agent >> Edge(label="CreateEvent") >> events
    agent >> Edge(label="ListEvents (直近文脈)") << events
    events >> Edge(style="dashed", label="非同期抽出\n(namespace で分離)") >> records
    agent >> Edge(label="RetrieveMemoryRecords\n(セマンティック検索)") << records


# 3. Gateway -----------------------------------------------------------------
with diagram("AgentCore Gateway", "../assets/agentcore_gateway"):
    agent = Bedrock("エージェント\n(MCP クライアント)")
    with Cluster("AgentCore Gateway (MCP サーバ)"):
        gw = Bedrock("Inbound Authorizer\n+ セマンティックツール検索")
        with Cluster("Targets"):
            t_lambda = Lambda("Lambda")
            t_api = Internet("OpenAPI / Smithy")
            t_mcp = Bedrock("外部 MCP サーバ")
        cred = SecretsManager("Credential Provider\n(API キー / OAuth)")
    agent >> Edge(label="ListTools / InvokeTool") >> gw
    gw >> t_lambda
    gw >> t_api
    gw >> t_mcp
    gw >> Edge(style="dashed", label="Outbound 認証") >> cred


# 4. Identity ----------------------------------------------------------------
with diagram("AgentCore Identity", "../assets/agentcore_identity"):
    caller = Client("呼び出し元")
    with Cluster("Inbound Auth (排他)"):
        jwt = Cognito("OAuth JWT\n(Cognito 等)")
        sigv4 = IAMRole("IAM SigV4")
    with Cluster("AgentCore Identity"):
        wl = IAMRole("Workload Identity\n(自動作成)")
        with Cluster("Token Vault (KMS 暗号化)"):
            vault = KMS("OAuth トークン /\nAPI キー")
    runtime = Bedrock("Runtime\n(エージェント)")
    ext = Internet("外部 SaaS\n(Google/GitHub 等)")
    caller >> Edge(label="Bearer JWT") >> jwt >> runtime
    caller >> Edge(style="dashed", label="or SigV4") >> sigv4 >> runtime
    runtime >> Edge(label="Workload Access Token") >> wl >> vault
    vault >> Edge(style="dotted", label="2LO / 3LO") >> ext


# 5. Observability -----------------------------------------------------------
with diagram("AgentCore Observability", "../assets/agentcore_observability"):
    with Cluster("AgentCore Runtime"):
        agent = Fargate("エージェント\n(ADOT 自動計装)")
    with Cluster("Amazon CloudWatch"):
        spans = CloudwatchLogs("Transaction Search\n(aws/spans)")
        metrics = Cloudwatch("メトリクス\n(bedrock-agentcore)")
        logs = CloudwatchLogs("APPLICATION_LOGS\n(trace_id / span_id)")
        dash = Cloudwatch("GenAI Observability\n(Agents/Sessions/Traces)")
    trail = Cloudtrail("CloudTrail")
    agent >> Edge(label="OTEL spans") >> spans >> dash
    agent >> Edge(label="metrics") >> metrics >> dash
    agent >> Edge(label="logs") >> logs >> dash
    agent >> Edge(style="dotted") >> trail
