# Kubernetes Resource Monitoring

## Introduction

I build this project to understand with hands on learning platform for Kubernetes and the surrounding ecosystem. Rather than focusing on a single application, the goal was to understand how Kubernetes, Helm, GitHub Actions, GHCR, Argo CD, Prometheus, and Grafana interact in a complete GitOps workflow. To achieve this, I developed a Python based exporter that collects Kubernetes workload data and exposes it as Prometheus metrics, which are then visualized in Grafana dashboard.

## Architecture

This project is tested in two different local Kubernetes environments, Docker Desktop Kubernetes at home and a kind cluster running on WSL2 at the office. The office environment has experienced TLS related connectivity issues when accessing both GHCR and Git repositories. Because of this, container images are currently pulled and loaded into the cluster manually, and Argo CD is configured to bypass Git certificate verification as a temporary workaround.


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
<summary>Why did I design it like that?</summary>

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
<summary>Corporate TLS Restrictions Across GitOps Components</summary>
While working in the office environment, several tools failed with TLS certificate validation errors, including Git, Helm, and Argo CD. <br><br>

**Investigation**
- Git clone failed with certificate verification errors.
- Helm repository registration failed with x509 certificate validation errors.
- Argo CD could not connect to GitHub repositories.
- SSH based repository access was investigated but could not be used due to corporate restrictions.

**Attempts**
- Tested Git access with SSL verification disabled.
- Tested Helm repository access with `--insecure-skip-tls-verify`
- Configured `GIT_SSL_NO_VERIFY` in the Argo CD deployment.
- Created repository secrets manually.
- Investigated both annotations and labels used by Argo CD repository secrets.

**Findings** <br>
The corporate environment imposed TLS certificate restrictions that affected multiple Git based integrations.

**Resolution** <br>
Configured temporary TLS verification bypass mechanisms where required and corrected the repository secret configuration so that Argo CD could recognize and connect to the repository.

</details>


<details>
<summary>Prometheus Could Not Discover Exporter Metrics</summary>
Prometheus was unable to scrape metrics from the exporter even though the ServiceMonitor resource had been deployed successfully. <br><br>

**Investigation**
- Verified ServiceMonitor labels.
- Verified Prometheus selectors.
- Verified Service labels.
- Verified Pod labels.
- Checked endpoints:
```cli
kubectl get endpoints -n helm-monitor
```
- Observed that no endpoints were generated.

**Findings** <br>
The exporter Pod remained in `ImagePullBackOff` state.<br>
Because the Pod never became available, Kubernetes could not generate Service endpoints. <br>

**Resolution** <br>
Pulled the image manually and loaded it into the kind cluster, allowing the exporter pod to start successfully and exposing the expected endpoints.

</details>


<details>
<summary>Service Was Healthy But No Endpoints Were Created</summary>
After resolving image pull issues, the Service still did not generate endpoints. <br><br>

**Investigation**
- Verified Pod status.
- Rechecked Service selectors.
- Inspected generated Endpoints resources.
- Compared service ports and container ports.

**Findings** <br>
The Service targetPort did not match the containerPort exposed by the exporter. <br>

**Resolution** <br>
Corrected the Service configuration so that targetPort matched the exporter containerPort.

</details>


<details>
<summary>Pod Remained in READY 0/1 State</summary>
The exporter pod started successfully but never became Ready. <br><br>

**Investigation**
- Checked pod events
- Inspected readiness probe configuration
- Verified probe path and port configuration
- Confirmed the /readyz endpoint existed in the source code
- Compared deployed image versions with locally built images

**Findings** <br>
A locally cached image with the latest tag was being reused instead of the newly built image. <br>
As a result, the running container did not contain the expected application changes. <br>

**Resolution** <br>
Updated the deployment workflow to reference *SHA* tagged images instead of relying on the *latest* tag, preventing stale cached images from being reused.

</details>


<details>
<summary>Argo CD Could Not Connect to GitHub Repository</summary>
Argo CD failed to register the Git repository required for GitOps synchronization. <br><br>

**Investigation**
- Tested HTTPS access
- Tested SSH based authentication
- Created repository secrets manually
- Verified Argo CD repository resources
- Inspected generated Kubernetes secrets
- Compared labels and annotations used by working and non working repository definitions

**Findings**
The repository secret was created incorrectly and was not recognized as an Argo CD repository secret. <br>
In addition, several fields had been placed under annotations instead of their expected locations. <br>

**Resolution** <br>
Added the correct repository secret label and corrected the secret structure so that Argo CD could load the Git repository successfully.

</details>

