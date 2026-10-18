from kubernetes import client, config

config.load_kube_config()

v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces().items

for pod in pods:
  ns = pod.metadata.namespace
  pod_name = pod.metadata.name
  containers = pod.spec.containers

  for container in containers:
    image = container.image
    print(f"The pod name is {pod_name}")
    print(f"The namespace is {ns}")
    print(f"The image is {image}")
