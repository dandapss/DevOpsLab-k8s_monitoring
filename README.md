# Kubernetes Resource Monitoring

## Introduction

A personal project for collecting Kubernetes resource and Warning-event metrics. A Python exporter reads cluster information and exposes it to Prometheus. The project uses GitHub Actions, GHCR, Helm, and Argo CD to deliver the application to two local Kubernetes labs.

## Architecture

```mermaid
flowchart TB
  subgraph L[Local labs]
    H[Home<br/>Docker Desktop + Docker Desktop Kubernetes]
    W[Company<br/>Docker Desktop + WSL2 + kind<br/>GitHub TLS validation is temporarily disabled]
  end

  H -->|edit · commit · push| G[GitHub<br/>source · Helm chart · manifests]
  W -->|edit · commit · push| G

  G --> A[GitHub Actions<br/>validate changes · build and scan image when needed]
  A -->|push exporter image| R[GHCR]
  A -.->|commit updated image tag| G

  G -->|Argo CD reads Git| C1
  G -->|Argo CD reads Git| C2
  R -->|image pull| C1
  R -->|image pull| C2

  subgraph C1[Home cluster · Argo CD + Helm]
    API1[Kubernetes API] -. read-only RBAC .-> E1[Python exporter<br/>/metrics]
    S1[ServiceMonitor] -. discovers endpoint .-> P1[Prometheus]
    P1 -->|scrapes /metrics| E1
    F1[Grafana] -->|queries| P1
  end

  subgraph C2[Company cluster · kind on WSL2 · Argo CD + Helm]
    API2[Kubernetes API] -. read-only RBAC .-> E2[Python exporter<br/>/metrics]
    S2[ServiceMonitor] -. discovers endpoint .-> P2[Prometheus]
    P2 -->|scrapes /metrics| E2
    F2[Grafana] -->|queries| P2
  end

  classDef lab fill:#eaf2fb,stroke:#8eacca,color:#202b3c
  classDef source fill:#e9edf2,stroke:#aab5c2,color:#202b3c
  classDef ci fill:#eee9f7,stroke:#b6a2d1,color:#202b3c
  classDef registry fill:#e8f3ed,stroke:#96bba1,color:#202b3c
  classDef monitor fill:#fff4e6,stroke:#d8b77e,color:#202b3c
  class H,W lab
  class G source
  class A ci
  class R registry
  class E1,API1,S1,P1,F1,E2,API2,S2,P2,F2 monitor
```

## Dashboard

<details>
<summary>Grafana dashboard screenshots</summary>

[Dashboard JSON](kubernetes/grafana/dashboard.json)

<img width="1617" height="479" alt="Dashboard_Panel_00" src="https://github.com/user-attachments/assets/c85779b7-8935-471d-80c3-e2bd6d75a570" />

<img width="1636" height="908" alt="Dashboard_Panel_01" src="https://github.com/user-attachments/assets/3ded5afa-32aa-428f-8cf6-3df30729c83e" />

<img width="1625" height="552" alt="Dashboard_Panel_02" src="https://github.com/user-attachments/assets/349b3a48-98bb-4a95-8134-777c20fcdbf6" />

<img width="1625" height="584" alt="Dashboard_Panel_03" src="https://github.com/user-attachments/assets/e7a9eecb-17e4-4538-8599-fd4aaf34254d" />

</details>

## Troubleshooting

<details>
<summary>Issues resolved during the project</summary>

- **Exporter returned 403:** added a dedicated ServiceAccount and read-only RBAC permissions.
- **Prometheus showed no exporter targets:** aligned the Service label with the ServiceMonitor selector.
- **node-exporter restarted in Docker Desktop:** disabled its host root filesystem mount for the local lab.
- **Exporter HTTP server failed to start:** corrected the server initialization and rebuilt the image.
- **Prometheus image inspection failed:** switched from the distroless image variant to the standard image.

More context is in [Troubleshoot.md](Troubleshoot.md).

</details>

## What I learned

<details>
<summary>Local containers and Kubernetes labs</summary>

- Set up separate home and company labs with Docker Desktop Kubernetes and kind on WSL2.
- Built and published a Python exporter image to GHCR.

</details>

<details>
<summary>GitHub Actions and GitOps</summary>

- Used GitHub Actions to validate changes and build the image only for relevant source changes.
- Added image scanning and Helm image tag updates to the delivery flow.
- Connected the Helm deployment to Argo CD so cluster state is managed from Git.

</details>

<details>
<summary>Prometheus and Grafana</summary>

- Exposed exporter metrics and configured Prometheus discovery through a ServiceMonitor.
- Practiced PromQL queries, including handling duplicate series with `max without`.
- Explored Grafana panels using the metrics collected by the project.

</details>
