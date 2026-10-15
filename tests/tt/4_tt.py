from kubernetes import client, config
from prometheus_client import Gauge

config.load_kube_config()

v1 = client.CoreV1Api()
apps1 = client.AppsV1Api()

pods = v1.list_pod_for_all_namespaces().items
deployments = apps1.list_deployment_for_all_namespaces().items

deploy_info = Gauge(
  "p_deploy_info",
  "yeaaaaahhhh",
  ["namespace", "deploy_name", "replica", "readyReplica", "rate"]
  )

pod_info = Gauge(
  "k8s_pod_info",
  "Whateeeeeever",
  ["namespace", "pod_name", "image", "state"]
  )

d_output = ["NAMESPACE  |  DEPLOYMENT  |  HEALTH"]
for deployment in deployments:
  namespace = deployment.metadata.namespace
  deploy_name = deployment.metadata.name
  replica = deployment.spec.replicas
  readyReplica = deployment.status.ready_replicas
  rate = readyReplica / replica * 100

  deploy_info.labels(
    namespace = deployment.metadata.namespace,
    deploy_name = deploy_name,
    replica = replica,
    readyReplica = readyReplica
    ).set(rate)
  
  d_output.append(f"{namespace} | {deploy_name} | {rate}%")
  
for pod in pods:
  namespace = pod.metadata.namespace
  pod_name = pod.metadata.name
  state = pod.status.phase
  containers = pod.spec.containers

  for container in containers:
    image = container.image

    pod_info.labels(
      namespace = namespace,
      pod_name = pod_name,
      image = image,
      state = state
      ).set(1)

print("Do you want to check the deployment health?")
Ans = input("Y or N :")
if Ans.upper() == "Y" or "YES":
  print("\n".join(d_output))
  print()
  
