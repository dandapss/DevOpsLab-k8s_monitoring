"""Read-only Kubernetes resource exporter for Prometheus."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from urllib.parse import urlsplit

from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest


try:
    config.load_incluster_config()
except ConfigException:
    # Allows local development with the user's current kubeconfig.
    config.load_kube_config()

core_api = client.CoreV1Api()
apps_api = client.AppsV1Api()
registry = CollectorRegistry()
metrics_lock = Lock()

pods_by_phase = Gauge(
    "k8s_pods", "Number of pods by namespace and phase", ["namespace", "phase"], registry=registry
)
nodes_total = Gauge("k8s_nodes_total", "Total number of nodes", registry=registry)
nodes_ready = Gauge("k8s_nodes_ready", "Number of Ready nodes", registry=registry)
namespaces_total = Gauge("k8s_namespaces_total", "Total number of namespaces", registry=registry)
namespace_resources = Gauge(
    "k8s_namespace_resources",
    "Number of supported resources in a namespace",
    ["namespace", "resource"],
    registry=registry,
)
deployment_replicas = Gauge(
    "k8s_deployment_replicas",
    "Deployment replica counts by namespace and deployment",
    ["namespace", "deployment", "state"],
    registry=registry,
)


def collect_metrics():
    """Refresh metrics from live API objects; values in manifest files are not assumed."""
    pods = core_api.list_pod_for_all_namespaces(_request_timeout=5).items
    nodes = core_api.list_node(_request_timeout=5).items
    namespaces = core_api.list_namespace(_request_timeout=5).items
    deployments = apps_api.list_deployment_for_all_namespaces(_request_timeout=5).items
    services = core_api.list_service_for_all_namespaces(_request_timeout=5).items
    config_maps = core_api.list_config_map_for_all_namespaces(_request_timeout=5).items

    # Clear labeled series so deleted objects/namespaces disappear from Prometheus.
    pods_by_phase.clear()
    namespace_resources.clear()
    deployment_replicas.clear()

    pod_counts = {}
    for pod in pods:
        namespace = pod.metadata.namespace or "default"
        phase = pod.status.phase or "Unknown"
        pod_counts[(namespace, phase)] = pod_counts.get((namespace, phase), 0) + 1
    for (namespace, phase), count in pod_counts.items():
        pods_by_phase.labels(namespace, phase).set(count)

    nodes_total.set(len(nodes))
    nodes_ready.set(
        sum(
            1
            for node in nodes
            if any(c.type == "Ready" and c.status == "True" for c in (node.status.conditions or []))
        )
    )
    namespaces_total.set(len(namespaces))

    resource_counts = {}
    for resource, objects in (("deployments", deployments), ("services", services), ("configmaps", config_maps)):
        for obj in objects:
            namespace = obj.metadata.namespace or "default"
            resource_counts[(namespace, resource)] = resource_counts.get((namespace, resource), 0) + 1
    for (namespace, resource), count in resource_counts.items():
        namespace_resources.labels(namespace, resource).set(count)

    for deployment in deployments:
        namespace = deployment.metadata.namespace or "default"
        name = deployment.metadata.name
        status = deployment.status
        spec = deployment.spec
        deployment_replicas.labels(namespace, name, "desired").set(spec.replicas or 0)
        deployment_replicas.labels(namespace, name, "ready").set(status.ready_replicas or 0)
        deployment_replicas.labels(namespace, name, "available").set(status.available_replicas or 0)

    return {
        "pods": pods,
        "nodes": nodes,
        "namespaces": namespaces,
        "deployments": deployments,
        "services": services,
        "configmaps": config_maps,
    }


def cluster_summary(snapshot):
    pods = snapshot["pods"]
    nodes = snapshot["nodes"]
    ready = sum(
        1
        for node in nodes
        if any(c.type == "Ready" and c.status == "True" for c in (node.status.conditions or []))
    )
    phases = {}
    for pod in pods:
        phase = pod.status.phase or "Unknown"
        phases[phase] = phases.get(phase, 0) + 1
    return (
        f"Namespaces: {len(snapshot['namespaces'])}\n"
        f"Pods: {len(pods)} (" + ", ".join(f"{k}={v}" for k, v in sorted(phases.items())) + ")\n"
        f"Nodes: {len(nodes)} (Ready={ready})\n"
        f"Deployments: {len(snapshot['deployments'])}\n"
        f"Services: {len(snapshot['services'])}\n"
        f"ConfigMaps: {len(snapshot['configmaps'])}\n"
    ).encode()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/":
            self._respond(200, b"Kubernetes Monitor\n/healthz /readyz /cluster /metrics\n")
        elif path == "/healthz":
            self._respond(200, b"OK\n")
        elif path == "/readyz":
            try:
                core_api.list_namespace(limit=1, _request_timeout=5)
                self._respond(200, b"Ready\n")
            except client.ApiException:
                self._respond(503, b"Kubernetes API unavailable\n")
            except Exception:
                self._respond(503, b"Kubernetes API unavailable\n")
        elif path in ("/cluster", "/metrics"):
            try:
                # Gauges are refreshed in place; serialize refreshes and scrape output.
                with metrics_lock:
                    snapshot = collect_metrics()
                    output = generate_latest(registry) if path == "/metrics" else None
            except client.ApiException:
                self._respond(503, b"Kubernetes API request failed\n")
                return
            except Exception:
                self._respond(503, b"Kubernetes API request failed\n")
                return

            if path == "/cluster":
                self._respond(200, cluster_summary(snapshot))
            else:
                self._respond(200, output, CONTENT_TYPE_LATEST)
        else:
            self._respond(404, b"Not Found\n")

    def _respond(self, status, body, content_type="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("Kubernetes Monitor running on port 8080", flush=True)
    server.serve_forever()
