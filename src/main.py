# 웹 서버 기능 제공
from http.server import BaseHTTPRequestHandler, HTTPServer

# Kubernetes API 사용
from kubernetes import client, config

# Prometheus Metric 생성
from prometheus_client import (
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST
)

# 현재 Pod 내부에서 실행중이라고 가정
# ServiceAccount 정보를 이용해 K8S API 접속
config.load_incluster_config()

# CoreV1 API 객체 생성
v1 = client.CoreV1Api()

# =======================================
# Prometheus Metrics 정의
# =======================================

# 전체 Pod 수
pods_total = Gauge(
    "k8s_pods_total",
    "Total number of pods"
)

# Running 상태 Pod 수
pods_running = Gauge(
    "k8s_pods_running",
    "Running pods"
)

# Pending 상태 Pod 수
pods_pending = Gauge(
    "k8s_pods_pending",
    "Pending pods"
)

# Failed 상태 Pod 수
pods_failed = Gauge(
    "k8s_pods_failed",
    "Failed pods"
)

# 전체 Node 수
nodes_total = Gauge(
    "k8s_nodes_total",
    "Total number of nodes"
)

# Ready 상태 Node 수
nodes_ready = Gauge(
    "k8s_nodes_ready",
    "Ready nodes"
)

# 전체 Namespace 수
namespaces_total = Gauge(
    "k8s_namespaces_total",
    "Total number of namespaces"
)


# =======================================
# 메트릭 수집 함수
# =======================================
def collect_metrics():

    # 모든 Namespace의 Pod 조회
    pods = v1.list_pod_for_all_namespaces().items

    # 전체 Pod 수
    pods_total.set(len(pods))

    # Running 상태 Pod 수 계산
    pods_running.set(
        sum(
            1 for pod in pods
            if pod.status.phase == "Running"
        )
    )

    # Pending 상태 Pod 수 계산
    pods_pending.set(
        sum(
            1 for pod in pods
            if pod.status.phase == "Pending"
        )
    )

    # Failed 상태 Pod 수 계산
    pods_failed.set(
        sum(
            1 for pod in pods
            if pod.status.phase == "Failed"
        )
    )

    # 모든 Node 조회
    nodes = v1.list_node().items

    # 전체 Node 수
    nodes_total.set(len(nodes))

    ready_nodes = 0

    # Node Condition 확인
    for node in nodes:

        for condition in node.status.conditions:

            # Ready=True인 Node만 카운트
            if (
                condition.type == "Ready"
                and condition.status == "True"
            ):
                ready_nodes += 1

    nodes_ready.set(ready_nodes)

    # Namespace 전체 조회
    namespaces = v1.list_namespace().items

    # Namespace 수 저장
    namespaces_total.set(len(namespaces))


# =======================================
# HTTP 요청 처리
# =======================================
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        # -----------------------------------
        # /
        # 메인 페이지
        # -----------------------------------
        if self.path == "/":

            message = b"""Kubernetes Monitor

Available Endpoints:
/
/healthz
/cluster
/metrics
"""

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain"
            )
            self.end_headers()

            self.wfile.write(message)

        # -----------------------------------
        # /healthz
        # Health Check
        # -----------------------------------
        elif self.path == "/healthz":

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain"
            )
            self.end_headers()

            self.wfile.write(b"OK")

        # -----------------------------------
        # /cluster
        # 사람이 보기 쉬운 상태 요약
        # -----------------------------------
        elif self.path == "/cluster":

            pods = v1.list_pod_for_all_namespaces().items
            nodes = v1.list_node().items
            namespaces = v1.list_namespace().items

            running = sum(
                1
                for pod in pods
                if pod.status.phase == "Running"
            )

            pending = sum(
                1
                for pod in pods
                if pod.status.phase == "Pending"
            )

            failed = sum(
                1
                for pod in pods
                if pod.status.phase == "Failed"
            )

            ready_nodes = 0

            for node in nodes:

                for condition in node.status.conditions:

                    if (
                        condition.type == "Ready"
                        and condition.status == "True"
                    ):
                        ready_nodes += 1

            message = f"""
Namespaces : {len(namespaces)}

Pods Total : {len(pods)}
Pods Running : {running}
Pods Pending : {pending}
Pods Failed : {failed}

Nodes Total : {len(nodes)}
Nodes Ready : {ready_nodes}
""".encode()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/plain"
            )
            self.end_headers()

            self.wfile.write(message)

        # -----------------------------------
        # /metrics
        # Prometheus가 가져가는 Endpoint
        # -----------------------------------
        elif self.path == "/metrics":

            # K8S 정보 가져오기
            collect_metrics()

            # Prometheus 형식 생성
            output = generate_latest()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                CONTENT_TYPE_LATEST
            )
            self.end_headers()

            self.wfile.write(output)

        # -----------------------------------
        # 존재하지 않는 URL
        # -----------------------------------
        else:

            self.send_response(404)
            self.end_headers()


# =======================================
# 웹 서버 시작
# =======================================

server = HTTPServer(
    ("0.0.0.0", 8080),
    Handler
)

print("Kubernetes Monitor running on port 8080")

# 무한 대기
server.serve_forever()
