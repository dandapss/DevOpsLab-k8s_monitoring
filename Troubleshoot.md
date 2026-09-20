1. Python HTTP Server Error

The first Docker version had an HTTPServer constructor issue.

The application was corrected and rebuilt.

Image versions were developed incrementally:

0.1.0
0.2.1
0.3.0

The final version currently used by Kubernetes is:

k8s-monitoring:0.3.0
2. Kubernetes RBAC 403 Error

Initially, the exporter used the default ServiceAccount.

Prometheus exporter logs showed:

pods is forbidden:
User "system:serviceaccount:minilab:default"
cannot list resource "pods"
at the cluster scope

The problem was solved by creating a dedicated ServiceAccount and RBAC configuration.

After applying the RBAC configuration, permission verification returned:

yes
3. Prometheus ImageInspectError

Prometheus initially failed with an image inspection error related to the distroless Prometheus image.

The problematic image was based on:

quay.io/prometheus/prometheus:v3.14.0-distroless

Prometheus was changed to the non-distroless image:

quay.io/prometheus/prometheus:v3.14.0

Command:

helm upgrade monitoring prometheus-community/kube-prometheus-stack `
  --reuse-values `
  --set prometheus.prometheusSpec.image.tag=v3.14.0

Prometheus then started successfully.

4. node-exporter CrashLoopBackOff

node-exporter initially had a problem related to the Docker Desktop host filesystem mount.

The following configuration was used:

helm upgrade monitoring prometheus-community/kube-prometheus-stack `
  --reuse-values `
  --set prometheus-node-exporter.hostRootFsMount.enabled=false

After the change, the monitoring stack became healthy.

5. ServiceMonitor showed 0/0 targets

Initially Prometheus showed:

serviceMonitor/monitoring/k8s-monitoring/0
0 / 0 up
No targets

The ServiceMonitor itself was being selected by Prometheus, but it could not find the target Service.

The problem was that the Service did not have the metadata label:

app: k8s-monitoring

The ServiceMonitor expected this label.

After adding the label to the Service:

metadata:
  labels:
    app: k8s-monitoring

Prometheus successfully discovered the target.

Docker Cleanup

Unused Docker images, build cache, and unused volumes were removed during the lab.

Commands used:

docker builder prune -a
docker image prune -a
docker volume prune

After cleanup:

Images:       20
Build Cache:  0B
Volumes:      0
