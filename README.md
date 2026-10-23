# Kubernetes Resource Monitoring

## Introduction

A personal Kubernetes monitoring project that collects cluster resource and Warning-event metrics. A Python exporter makes the metrics available to Prometheus. The project is developed in two local labs and uses GitHub Actions, GHCR, Helm, and Argo CD for delivery.

## Architecture

<table>
  <tr><th colspan="2">LOCAL DEVELOPMENT</th></tr>
  <tr>
    <td bgcolor="#eef4fa"><b>Home</b><br>Docker Desktop<br>Docker Desktop Kubernetes</td>
    <td bgcolor="#f4eff8"><b>Company</b><br>Docker Desktop · WSL2 · kind<br><br><b>GitHub TLS certificate validation fails here.</b><br>TLS verification is temporarily disabled in this lab.</td>
  </tr>
  <tr><td colspan="2" align="center">↓ <b>Git</b> · edit → commit → push</td></tr>
  <tr><td colspan="2" align="center" bgcolor="#eef1f5"><b>GitHub</b></td></tr>
  <tr><td colspan="2" align="center">↓</td></tr>
  <tr><td colspan="2" align="center" bgcolor="#f2eefa"><b>GitHub Actions</b></td></tr>
  <tr><td colspan="2" align="center">↓ image build and scan · image tag update ↗ GitHub</td></tr>
  <tr><td colspan="2" align="center" bgcolor="#f2eefa"><b>GHCR</b></td></tr>
  <tr><th colspan="2">DEPLOYMENT TARGETS</th></tr>
  <tr>
    <td bgcolor="#eef4fa"><b>Home cluster</b><br>Argo CD · Helm<br>Docker Desktop Kubernetes</td>
    <td bgcolor="#f4eff8"><b>Company cluster</b><br>Argo CD · Helm<br>kind on WSL2</td>
  </tr>
  <tr><td colspan="2" align="center">GitHub → Argo CD · GHCR → image pull</td></tr>
  <tr><th colspan="2">MONITORING FLOW · SAME IN EACH LAB</th></tr>
  <tr><td colspan="2" align="center" bgcolor="#faf1e5">Sample workloads → Kubernetes API</td></tr>
  <tr><td colspan="2" align="center">Python exporter ↔ Kubernetes API <small>(read-only)</small></td></tr>
  <tr><td colspan="2" align="center" bgcolor="#eaf2f8">Python exporter · /metrics</td></tr>
  <tr><td colspan="2" align="center">↓</td></tr>
  <tr><td colspan="2" align="center" bgcolor="#eaf2f8">ServiceMonitor</td></tr>
  <tr><td colspan="2" align="center">↓</td></tr>
  <tr><td colspan="2" align="center" bgcolor="#edf4ed">Prometheus → Grafana</td></tr>
</table>

## Troubleshooting

<details>
<summary>Issues resolved in the lab</summary>

- **Exporter returned 403:** replaced the default ServiceAccount with a dedicated ServiceAccount and read-only RBAC permissions.
- **ServiceMonitor showed 0/0 targets:** aligned the Service label with the ServiceMonitor selector.
- **node-exporter restarted in Docker Desktop:** disabled the host root filesystem mount for this local environment.
- **Exporter HTTP server failed to start:** corrected the server initialization and rebuilt the image.

See [Troubleshoot.md](Troubleshoot.md) for the longer notes.

</details>

## What I learned

<details>
<summary>Local labs and containers</summary>

- Set up a home lab with Docker Desktop Kubernetes and a company lab with WSL2 and kind.
- Build a container image for the exporter and publish it to GHCR.

</details>

<details>
<summary>Git, CI, and GitOps</summary>

- Use Git to track and push project changes from both environments.
- Configure GitHub Actions path filters so Kubernetes-only changes do not build an image.
- Validate YAML and Helm, scan source-built images with Trivy, and update the Helm image tag.
- Connect a Helm chart to Argo CD for deployment from Git.

</details>

<details>
<summary>Prometheus and Grafana</summary>

- Expose Kubernetes resource metrics from a Python exporter and discover it through a ServiceMonitor.
- Use PromQL, including `max without`, to handle duplicate series.
- Build Grafana panels from PromQL for workload status, restarts, and Warning events.

</details>
