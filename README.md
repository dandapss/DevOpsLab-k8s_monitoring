# Kubernetes Resource Monitoring

## Introduction

A personal Kubernetes monitoring project that collects cluster resource and Warning-event metrics. A Python exporter makes the metrics available to Prometheus. Helm and Argo CD handle deployment, while GitHub Actions validates changes and delivers exporter images.

## Architecture

```mermaid
flowchart TB
  classDef source fill:#eef1f5,stroke:#667085,color:#202939
  classDef delivery fill:#f1eafa,stroke:#7856a6,color:#33224a
  classDef runtime fill:#eaf2f8,stroke:#477a9e,color:#18364a
  classDef monitoring fill:#edf4ed,stroke:#5b805e,color:#29432b
  classDef sample fill:#faf1e5,stroke:#a87937,color:#4d391e

  subgraph code[Source and delivery]
    direction TB
    repo[GitHub repository]:::source
    actions[GitHub Actions<br/>YAML and Helm checks]:::delivery
    image[GHCR image<br/>built for exporter changes]:::delivery
    repo --> actions
    actions -->|Exporter source changed| image
    actions -.->|Update image tag| repo
  end

  subgraph lab[Kubernetes cluster]
    direction TB
    argocd[Argo CD<br/>Helm chart from Git]:::delivery
    exporter[Python exporter]:::runtime
    workloads[Sample workloads]:::sample
    api[Kubernetes API]:::runtime
    prometheus[Prometheus]:::monitoring
    grafana[Grafana]:::monitoring
    argocd --> exporter
    image -->|Pull image| exporter
    workloads --> api
    exporter -->|Read cluster resources| api
    exporter -->|/metrics| prometheus
    prometheus --> grafana
  end

  repo -->|Tracks deployment config| argocd
```

## Troubleshooting

<details>
<summary>Health and readiness checks</summary>

The exporter uses `/healthz` for liveness and `/readyz` to check Kubernetes API access before receiving traffic.

</details>

## What I learned

<details>
<summary>Kubernetes and deployment</summary>

- Deploy workloads with Kubernetes and package the exporter with Helm.
- Configure API access with RBAC and health checks with probes.
- Use Argo CD to reconcile a Helm deployment from Git.

</details>

<details>
<summary>CI/CD and monitoring</summary>

- Use GitHub Actions path filters to avoid image builds for Kubernetes-only changes.
- Build, scan, and publish container images to GHCR.
- Expose metrics to Prometheus with a ServiceMonitor and explore them with PromQL.

</details>
