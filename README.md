# DevOpsLab - Kubernetes Monitoring

A DevOps learning project for building a Kubernetes monitoring environment with a Python-based Kubernetes exporter, Prometheus, and Grafana.

The project is running on Docker Desktop Kubernetes.

## Architecture

```text
Developer
   │
   ▼
Application
   │
   ▼
Docker
   │
   ▼
Kubernetes
   │
   ├── Python Kubernetes Exporter
   │      └── Kubernetes API
   │
   ├── Service
   │      └── /metrics
   │
   ├── ServiceMonitor
   │      └── Prometheus scraping
   │
   ├── Prometheus
   │
   └── Grafana
```

Environment
- Windows
- Docker Desktop
- Docker Desktop Kubernetes
- Kubernetes
- kubectl
- Helm
- Python 3.12
- Docker
- Prometheus
- Grafana
- kube-prometheus-stack

Project Structure
k8s-monitoring/
├── .gitignore
├── Dockerfile
├── deployment.yaml
├── rbac.yaml
├── requirements.txt
├── service-monitor.yaml
├── service.yaml
├── test-apps.yaml
└── src/
    └── main.py

1. Python Kubernetes Exporter

A simple Python exporter was created to communicate with the Kubernetes API.
- The exporter provides: /
- Basic application health cehck: /pods
- Lists Pods across all namespaces: /metrics

Provides Prometheus metrics.
The main custom metric currently implemented is: k8s_pod_count


2. Docker
The Python exporter was containerized using Docker.

Dockerfile:
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/main.py .

EXPOSE 8080

CMD ["python", "main.py"]

Current local image: k8s-monitoring:0.3.0
The image was tested locally before being deployed to Kubernetes.


3. Kubernetes Deployment
The exporter runs as a Kubernetes Deployment.

The Deployment uses:
 ServiceAccount: k8s-monitoring
 Namespace: minilab

*As the project currently runs on Docker Desktop Kubernetes, the Deployment uses "imagePullPolicy: Never"
>> This allows Kubernetes to use the locally built Docker image.


4. Kubernetes RBAC
The Python exporter needs access to the Kubernetes API.

A ServiceAccount, ClusterRole, and CluserRoleBidning were configured.

The exporter currently has permission to "get" and "list" for "pods"

This was intentionally configured with limited permissions instead of using cluster-admin


5. Kubernetes Service
- A Kubernetes Service exposes the exporter on port 8080
- The Service selects the exporter Pod using: selector.app:k8s-monitoring
- The Service has the following metadata label: labels.app:k8s-monitoring



