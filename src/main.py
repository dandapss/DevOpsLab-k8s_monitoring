# Made by Me with little help of GPT
# Last Update 18th of Oct. 2026

import time
from kubernetes import client, config
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from threading import Lock


config.load_incluster_config()

v1 = client.CoreV1Api()
apps1 = client.AppsV1Api()

#-------------#
# Gauge Start #
#-------------#
registry = CollectorRegistry()

pods_info = Gauge(
  "k8s_pods",
  "Pods Info",
  ["Namespace", "Pod_Name", "Image", "State"],
  registry = registry
  )

deploy_info = Gauge(
  "k8s_deploy",
  "Deploys Info",
  ["Namespace", "Deploy_Name"],
  registry = registry
  )

namespace_info = Gauge(
  "k8s_namespace",
  "Namespaces Info",
  ["NS_Name", "State"],
  registry = registry
  )

metrics_lock = Lock()

#-----------#
# Gague End #
#-----------#


#-------------#
# Label Start #
#-------------#

def collect_metrics():

  pods = v1.list_pod_for_all_namespaces().items
  deployments = apps1.list_deployment_for_all_namespaces().items
  namespaces = v1.list_namespace().items

  pods_info.clear()
  deploy_info.clear()
  namespace_info.clear()

  for pod in pods:
    Seob_Namespace = pod.metadata.namespace
    Seob_Pod_Name = pod.metadata.name
    Seob_State = pod.status.phase or "Unknown"
    Seob_containers = pod.spec.containers
    for container in Seob_containers:
      Image = container.image

      pods_info.labels(
        Namespace = Seob_Namespace,
        Pod_Name = Seob_Pod_Name,
        State = Seob_State,
        Image = Image
        ).set(1)

  for deploy in deployments:
    Seob_Namespace = deploy.metadata.namespace
    Seob_Deploy_Name = deploy.metadata.name
    Seob_replica = deploy.spec.replicas or 0
    Seob_readyReplica = deploy.status.ready_replicas or 0

    if Seob_replica > 0:
      rate = Seob_readyReplica / Seob_replica * 100
    else:
      rate = 999

    deploy_info.labels(
      Namespace = Seob_Namespace,
      Deploy_Name = Seob_Deploy_Name,
      ).set(rate)

  for namespace in namespaces:
    Seob_NS_Name = namespace.metadata.name
    Seob_State= namespace.status.phase or "Unknown"

    namespace_info.labels(
      NS_Name = Seob_NS_Name,
      State = Seob_State
      ).set(1)

#-----------#
# Label End #
#-----------#


#--------------------#
# HTTP Request Start #
#--------------------#

class What_To_Get(BaseHTTPRequestHandler):

  def do_GET(self):
    path = urlsplit(self.path).path

    if path == "/healthz":
      self.respond(200, b"OK\n")
      return

    if path == "/metrics":
      try:
        with metrics_lock:
          collect_metrics()
          output = generate_latest(registry)

        self.respond(200, output, CONTENT_TYPE_LATEST)

      except Exception as e:
        print(f"Metric collection failed: {e}", flush=True)
        self.respond(503, b"Metric collection failed\n")

      return

    self.respond(404, b"Not Found\n")

  def respond(self, status, body, content_type="text/plain; charset=utf-8"):
    self.send_response(status)
    self.send_header("Content-Type", content_type)
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

#------------------#
# HTTP Request End #
#------------------#


#-----------#
# Run Start #
#-----------#

if __name__ == "__main__":
  server = ThreadingHTTPServer(("0.0.0.0", 8080), What_To_Get)
  print("Kubernetes exporter running on port 8080", flush=True)
  server.serve_forever()

#---------#
# Run End #
#---------#

