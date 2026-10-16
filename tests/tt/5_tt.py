from kubernetes import client, config
from prometheus_client import Gauge

config.load_kube_config()

v1 = client.CoreV1Api()
apps1 = client.AppsV1Api()

pods = v1.list_pod_for_all_namespaces().items
deployments = apps1.list_deployment_for_all_namespaces().items
namespaces = v1.list_namespace.items

#-------------#
# Gauge Start #
#-------------#

pods_info = Gauge(
  "k8s_pods",
  "Pods Info",
  ["Namespace", "Pod_Name", "Image", "State"]
  )

deploy_info = Gauge(
  "k8s_deploy",
  "Deploys Info",
  ["Namespace", "Deploy_Name", "State"]
  )

deploy_health = Gauge(
  "k8s_deploy_health",
  "Deployments Ready Rate",
  ["Namespace", "Deploy_Name"]
  )

namespace_info = Gague(
  "k8s_namespace",
  "Namespaces Info",
  ["NS_Name", "State"]
  )

#-----------#
# Gague End #
#-----------#



#-------------#
# Label Start #
#-------------#

for pod in pods:
  Namespace = pod.metadata.namespace
  Pod_Name = pod.metadata.name
  State = pod.status.phase
  containers = pod.spec.containers
  for container in containers:
    Image = container.image

    pods_info.labels(
      Namespace = Namespace,
      Pod_Name = Pod_Name,
      State = State,
      Image = Image
      ).set(1)

for deploy in deployments:
  Namespace = deploy.metadata.namespace
  Deploy_name = deploy.metadata.name
  State = deploy.status.phase
  replica = deploy.spec.replicas
  readyReplica = deploy.status.ready_replicas

  if replica > 0:
    rate = readyReplica / replica * 100
  else:
    rate = 100

  deply_info.labels(
    Namespace = Namespace,
    Deploy_Name = Deploy_Name,
    State = State
    ).set(1)

  deploy_health.labels(
    Namespace = Namespace,
    Deploy_Name = Deploy_Name,
    ).set(rate)

for namespace in namespaces:
  NS_Name = namespace.metadata.name
  State= namespace.status.phase

  namespace_info.labels(
    NS_Name = NS_Name,
    State = State
    ).set(len(namespaces))

#-----------#
# Label End #
#-----------#


