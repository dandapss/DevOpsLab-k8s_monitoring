from http.server import BaseHTTPRequestHandler, HTTPServer
from kubernetes import client, config
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST


config.load_incluster_config()

v1 = client.CoreV1Api()

pod_count = Gauge(
        "k8s_pod_count",
        "Number of pods in the cluster"
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            message = b"Kubernetes Monitor is running!\n"

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()

            self.wfile.write(message)

        elif self.path == "/pods":
            pods = v1.list_pod_for_all_namespaces()

            lines = []

            for pod in pods.items:
                lines.append(
                    f"{pod.metadata.namespace}/{pod.metadata.name}"
                )

            message = ("\n".join(lines) + "\n").encode()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()

            self.wfile.write(message)
        elif self.path == "/metrics":
            pods = v1.list_pod_for_all_namespaces()

            pod_count.set(len(pods.items))

            output = generate_latest()

            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(output)))
            self.end_headers()
            self.wfile.write(output)

        else:
            self.send_response(404)
            self.end_headers()


server = HTTPServer(("0.0.0.0", 8080), Handler)

print("Kubernetes Monitor running on port 8080")

server.serve_forever()
