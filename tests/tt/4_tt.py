from kubernetes import client, config
from prometheus_client import Gauge

config.load_kube_config()

v1 = client.CoreV1Api()
apps1 = client.AppsV1Api()

pods = v1.list_pod_for_all_namespaces().items
deployments = apps1.list_deployment_for_all_namespaces().items

deployment_health = Gauge(
  "k8s_deployment_health",
  "Deployment health percentage",
  ["namespace", "deployment"]
  )

d_output = ["NAMESPACE   |   DEPLOYMENT   |   HEALTH"]
for deployment in deployments:
  namespace = deployment.metadata.namespace
  deploy_name = deployment.metadata.name

  replica = deployment.spec.replicas or 0
  readyReplica = deployment.status.ready_replicas or 0

  if replica > 0:
    rate = readyReplica / replica * 100
  else:
    rate = 100

  deployment_health.labels(
    namespace = namespace,
    deployment = deploy_name
    ).set(rate)

  d_output.append(
    f"{namespace} | {deploy_name} | {rate:.0f}%"
    )

print("Check the deployment health?")
Ans = input("Y or N:")

if Ans.upper() in ("YES", "Y"):
  print("\n".join(d_output))
  print()
