# Kubernetes Resource Monitoring

## Introduction

A small Kubernetes monitoring lab. A Python exporter reads live cluster resources through the Kubernetes API and exposes metrics for Prometheus. Grafana is used to explore the metrics and build dashboards and alerts.

GitHub Actions validates the manifests and Helm chart. When exporter code or its build files change, it builds and scans a container image, publishes it to GHCR, and updates the Helm image tag. Argo CD deploys the chart to the local Kubernetes cluster.

## Architecture

```mermaid
flowchart LR
  classDef code fill:#E8EAF6,stroke:#3949AB,color:#1A237E,stroke-width:2px
  classDef delivery fill:#F3E5F5,stroke:#8E24AA,color:#4A148C,stroke-width:2px
  classDef cluster fill:#E3F2FD,stroke:#1E88E5,color:#0D47A1,stroke-width:2px
  classDef monitor fill:#E8F5E9,stroke:#43A047,color:#1B5E20,stroke-width:2px
  classDef sample fill:#FFF3E0,stroke:#FB8C00,color:#E65100,stroke-width:2px

  subgraph source[Code and delivery]
    direction LR
    repo[GitHub repository]:::code --> ci[GitHub Actions<br/>YAML and Helm checks]:::delivery
    ci -->|Exporter files changed| image[Build and Trivy scan]:::delivery
    image --> ghcr[GHCR image]:::delivery
    image --> tag[Update Helm image tag]:::delivery
    tag -->|Commit change| repo
  end

  subgraph lab[Docker Desktop Kubernetes]
    direction LR
    argocd[Argo CD<br/>Helm Application]:::delivery --> deploy[Exporter Deployment]:::cluster
    workloads[Sample workloads<br/>temp_app.yaml]:::sample --> api[Kubernetes API]:::cluster
    deploy --> exporter[Python exporter<br/>read-only resource access]:::cluster
    exporter -->|List pods, deployments,<br/>namespaces and Warning events| api
    exporter --> endpoint[ClusterIP Service<br/>/metrics]:::cluster
    endpoint --> sm[ServiceMonitor<br/>15-second scrape]:::monitor
    sm --> prometheus[Prometheus<br/>10-day retention · 500Mi PVC]:::monitor
    prometheus --> grafana[Grafana<br/>dashboard and alert work in progress]:::monitor
  end

  repo -->|Watches Helm chart| argocd
  ghcr -->|Pull image| deploy
```

`temp_app.yaml` creates sample resources in the cluster. The exporter reads the live Kubernetes API; it does not read that YAML file directly. Argo CD is configured to ignore Deployment image differences.

## Dashboard

<details>
<summary>Dashboard 1 — add title</summary>

<!-- Add a screenshot here when ready, for example: ![Dashboard](docs/images/dashboard-01.png) -->

- **Purpose:** Add a short description.
- **Panels and queries:** Add notes here.
- **Alerts:** Add rule and notification notes here.

</details>

<details>
<summary>Dashboard 2 — add title</summary>

<!-- Add a screenshot here when ready, for example: ![Dashboard](docs/images/dashboard-02.png) -->

- **Purpose:** Add a short description.
- **Panels and queries:** Add notes here.
- **Alerts:** Add rule and notification notes here.

</details>

## Troubleshooting

<details>
<summary>Issue — add a short title</summary>

- **Symptom:** What happened?
- **Cause:** What caused it?
- **Fix:** What resolved it?

</details>

## What I learned

<details>
<summary>Kubernetes and Helm</summary>

- Deploy workloads and inspect their state across namespaces.
- Package the exporter with Helm templates and values.
- Give the exporter read access through Kubernetes RBAC.
- Use `/healthz` for liveness and `/readyz` to check Kubernetes API access.

</details>

<details>
<summary>Metrics and monitoring</summary>

- Expose application metrics from Python at `/metrics`.
- Connect a Service, ServiceMonitor, and Prometheus scrape configuration.
- Use PromQL to handle duplicate series with `max without`.
- Check series count, retention, and storage when reviewing metric labels.

</details>

<details>
<summary>CI/CD and GitOps</summary>

- Use GitHub Actions path filters so Kubernetes-only changes do not build an image.
- Validate YAML and Helm charts in CI.
- Build, scan, and publish exporter images to GHCR when exporter build files change.
- Use Argo CD to track the Helm chart and reconcile the cluster with Git.

</details>
