# Made by Me with little help of GPT
# Last Update 25th of Oct. 2026

import time
from kubernetes import client, config
from prometheus_client import Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from threading import Lock
from datetime import datetime, timezone


config.load_incluster_config()
#config.load_kube_config()

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

pods_restart = Gauge(
  "pods_restart_count",
  "Pods Restarts",
  ["Namespace", "Pod_Name"],
  registry = registry
  )

pods_age = Gauge(
  "pod_age",
  "Pod Age",
  ["Namespace", "Pod_Name"],
  registry = registry
  )

resource_event_warning = Gauge(
  "k8s_resource_event",
  "Resource Events Only Warning",
  ["Namespace", "Resource", "Name", "Reason", "Message"],
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
  print("Logging Check!!!")
  pods = v1.list_pod_for_all_namespaces().items
  deployments = apps1.list_deployment_for_all_namespaces().items
  namespaces = v1.list_namespace().items
  events = v1.list_event_for_all_namespaces().items

  pods_info.clear()
  deploy_info.clear()
  namespace_info.clear()
  pods_restart.clear()
  pods_age.clear()
  resource_event_warning.clear()

  for pod in pods:
    Seob_Namespace = pod.metadata.namespace
    Seob_Pod_Name = pod.metadata.name
    Seob_State = pod.status.phase or "Unknown"
    Seob_containers = pod.spec.containers
    Seob_Pod_Restart = pod.status.container_statuses
    Seob_Pod_Created = pod.metadata.creation_timestamp

    restart_total = sum(status.restart_count for status in (Seob_Pod_Restart or []))
    pods_restart.labels(
      Namespace = Seob_Namespace,
      Pod_Name = Seob_Pod_Name
      ).set(restart_total)
    
    now = datetime.now(timezone.utc)
    age_time = now - Seob_Pod_Created
    age = age_time.total_seconds() / 3600
    pods_age.labels(
      Namespace = Seob_Namespace,
      Pod_Name = Seob_Pod_Name
      ).set(age)

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
      rate = -1

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

  for event in events:
    if event.type == "Warning":
      Seob_Namespace = event.involved_object.namespace
      Seob_Resource = event.involved_object.kind
      Seob_Name = event.involved_object.name
      Seob_Reason = event.reason
      Seob_Message = event.message

      resource_event_warning.labels(
        Namespace = Seob_Namespace,
        Resource = Seob_Resource,
        Name = Seob_Name,
        Reason = Seob_Reason,
        Message = Seob_Message
        ).set(event.count or 1)

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

    if path == "/readyz":
      try:
        v1.list_namespace(limit=1, _request_timeout=5)
        self.respond(200, b"All Ready!\n")
      except client.ApiException as e:
        print(f"ApiException: {e}", flush=True)
        self.respond(503, b"Kubernetes API unavailable\n")
      except Exception as e:
        print(f"Exception {e}", flush=True)
        self.respond(503, b"Kubernetes APi unavailable\n")

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

