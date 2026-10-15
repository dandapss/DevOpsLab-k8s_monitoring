from kubernetes import client, config
from prometheus_client import Gauge

config.load_kube_config()

v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces().items

pod_info = Gauge(
  "k8s_pod_info",
  "Whateeeeeever",
  ["namespace", "pod", "image", "state"]
  )

for pod in pods:
  
  namespace = pod.metadata.namespace
  name = pod.metadata.name
  state = pod.status.phase
  containers = pod.spec.containers
  
  for container in containers:
    image = container.image

    pod_info.labels(
      namespace = namespace,
      pod = name,
      image = image,
      state = state
      ).set(1)

    print(f"{pod_info}\n namespace : {namespace}\n pod name:  {name}\n pod status : {state}\n container image : {image}")
    print()
  
