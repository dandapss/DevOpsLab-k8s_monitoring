from kubernetes import client, config
from prometheus_client import Gauge

config.load_kube_config()

v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces().items

pod_info = Gauge(
  "k8s_pod_info",
  "Pod Information",
  ["namespace", "pod"]
  )

for pod in pods:
  pod_info.labels(
    namespace = pod.metadata.namespace,
    pod = pod.metadata.name
    ).set(1)
