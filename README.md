# Kubernetes Resource Monitoring

## Introduction

A personal Kubernetes monitoring project that collects cluster resource and Warning event metrics. A Python exporter exposes the data to Prometheus, with Grafana used for dashboards and alerting. The project uses Helm and Argo CD for deployment, and GitHub Actions for validation and image delivery.

Dashboard panels and alert rules are still being developed.

## Architecture

```mermaid
flowchart LR
  classDef source fill:#E8EAF6,stroke:#3949AB,color:#1A237E,stroke-width:2px
  classDef delivery fill:#F3E5F5,stroke:#8E24AA,color:#4A148C,stroke-width:2px
  classDef cluster fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:2px
  classDef monitoring fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:2px

  subgraph delivery[Code and delivery]
    repo[GitHub repository]:::source
    actions[GitHub Actions<br/>YAML and Helm validation]:::delivery
    ghcr[GHCR<br/>Exporter image]:::delivery
    argocd[Argo CD<br/>Helm deployment]:::delivery
    repo --> actions
    actions -->|Exporter changes: build, scan and publish| ghcr
    actions -->|Update image tag| repo
    repo -->|Track chart from Git| argocd
  end

  subgraph cluster[Local Kubernetes cluster]
    workload[Python exporter]:::cluster
    api[Kubernetes API]:::cluster
    service[Service<br/>/metrics]:::cluster
    prometheus[Prometheus]:::monitoring
    grafana[Grafana<br/>Dashboards and alerts]:::monitoring
    argocd --> workload
    ghcr -->|Pull image| workload
    workload -->|Read cluster resources| api
    workload --> service --> prometheus --> grafana
  end
```

## Dashboard

<details>
<summary>Dashboard and alerting</summary>

This section is reserved for final dashboard screenshots and a short explanation of the panels and alert rules.

</details>

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
