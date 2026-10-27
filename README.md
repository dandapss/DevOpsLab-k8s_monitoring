# Kubernetes Resource Monitoring

## Introduction

This project monitors Kubernetes with a Python exporter. It collects Pod status, image, age, and Pod-level restart counts; Deployment readiness; namespace status and Deployment counts; and Warning Events. Prometheus scrapes the exporter, and Grafana visualizes the metrics. GitHub Actions validates YAML and Helm, builds the image when its source or dependencies change, scans for fixable HIGH-severity vulnerabilities with Trivy, pushes the image to GHCR, and updates the Helm image tag. Argo CD syncs the chart from Git to my two local Kubernetes labs.

## Architecture

The home lab uses Docker Desktop Kubernetes and pulls the image from GHCR. The office lab uses WSL2 and kind. The red GHCR `ImagePullBackOff` path in the diagram shows the earlier office TLS workaround; the current image pull test succeeds. The `GIT_SSL_NO_VERIFY` setting in [Argo CD values](kubernetes/argocd/values.yaml) is separate: it temporarily skips certificate verification when Argo CD's repo-server fetches the Git repository. It does not control GHCR image pulls. GitHub Actions also runs Trivy between image build and push; that detail is omitted from this high-level diagram.

<img width="3408" height="4648" alt="Seob_Diagram_clear" src="https://github.com/user-attachments/assets/22c18414-14bb-4643-9d64-74e3abd3ec7a" />


## Dashboard

<details>
<summary>Grafana dashboard screenshots</summary>

[Dashboard JSON](kubernetes/grafana/dashboard.json)

<img width="1617" height="479" alt="Dashboard_Panel_00" src="https://github.com/user-attachments/assets/c85779b7-8935-471d-80c3-e2bd6d75a570" />

<img width="1636" height="908" alt="Dashboard_Panel_01" src="https://github.com/user-attachments/assets/3ded5afa-32aa-428f-8cf6-3df30729c83e" />

<img width="1625" height="552" alt="Dashboard_Panel_02" src="https://github.com/user-attachments/assets/349b3a48-98bb-4a95-8134-777c20fcdbf6" />

<img width="1625" height="584" alt="Dashboard_Panel_03" src="https://github.com/user-attachments/assets/e7a9eecb-17e4-4538-8599-fd4aaf34254d" />

</details>

## Design Decisions

<details>
<summary>What did I design it like that?</summary>

<details>
<summary> Exporter </summary>

1. Why implement custom metrics? <br>
     This project was created to gain hands on experience with a complete DevOps monitoring workflow. <br>
     Instead of relying only on existing Kubernetes metrics, I implemented a custom exporter to better understand:
      - How data is collected from the Kubernetes API
      - How metrics are exposed to Prometheus
      - How Prometheus stores and queries metrics
      - How Grafana visualizes operational data

2. Deployment Readiness Percentage <br>
     Deployment status is calculated as:
     ```python
     Ready Replicas / Desired Replicas * 100
     ```
    
     instead of simply checking whether the Deployment exists. <br>
     This allows operators to quickly identify the current deployment health status:
     |  Value  |  Meaning  |
     |---------|-----------|
     |   100   |  Fully Healthy |
     |  1-99   |  Requires Attention  |
     |    0    |  No Available Replica  |
     |   -1    |  Replica Information Unavailable  |

3. Pod Restart Count From a Pod Perspective  <br>
     Kubernetes provides restart counts per container. <br>
     Restart counts are aggregated at the Pod level: <br>
     ```python
     sum(status.restart_count for status in container_statuses)
     ```
     I added this because operational troubleshooting is typically performed from a Pod perspective rather than an individual container perspective.

4. Kubernetes API Based Readiness Check  <br>
     In Readiness probe, this exporter request 1 namespace instead of HTTP 200 response. <br>
     ```python
     v1.list_namespace(limit=1, _request_timeout=5)
     ```
     It verifies
     - Kubernetes API availability
     - Authentication status
     - RBAC permissions

</details>


<details>
<summary> Github Actions </summary>
     
1. Why use jobs.changes? <br>
     The pipeline uses path based filtering to determine whether a container image rebuild is required <br>
     It reduces
     - Unnecessary Docker builds
     - Unnecessary Trivy scans
     - Unnecessary image pushes
     Also it shortens CI execution time

2. Manifest Validation Before Image Build <br>
     It is performed before the Docker build stage
     - YAML validation (yamllint)
     - Helm validation (helm lint)
     This allows configuration errors to be detected early and prevents unnecessary image creation.

3. Dual Image Tag Strategy (SHA + latest) <br>
     Commit SHA
     - Immutable
     - Unique
     - Directly linked to a specific source code revision
     Latest
     - Easy reference for operators
     - Indicates the most recent successful build

4. GitOps Based Deployment <br>
     The pipeline does not directly deploy workloads to Kubernetes
     - Build Image → Push Image → Update Image tag in values.yaml → ArgoCD detects change → Deploy to Kubernetes <br>
     This keeps Git as the single source of truth and follows GitOps principles <br>
     The workflow also uses [skip ci] to prevent infinite CI loops when updating image tags automatically <br>

5. Why export Warning Events only? <br>
     - Normal Events were excluded because they generate large amounts of operational noise and provide limited value during incident investigations.
     - By focusing on Warning Events, the dashboard highlights actionable operational issues such as ImagePullBackOff, FailedScheduling, and FailedMount.

</details>


</details>

## Troubleshoot / Challenges

<details>
<summary>ImagePullBackOff in Kind Cluster</summary>
Symptom: Pods remained in ImagePullBackOff state after deployment. <br>
Investigation: 
   - Verified GHCR image existed
   - Tried curl in Pod to ghcr.io (TLS error)
   - It worked to load the image into kind cluster
Expecting cause: 
   - Kind node is running inside the contaienr runtime and it could not access to GHCR due to company security system
Resolution: Load images directly into the Kind cluster
   > docker image [image name:image tag] <br>
   > kind load docker-image [image name:image tag] --name [kind cluster name]

</details>


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
