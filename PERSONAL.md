Introduction
- This projects demonstrates from understanding basic concept of kubernetes infrastructure until configuring it.

Table of Contents
1. Project Overview
   1.1 What is this Project about?
   1.2 Key Features
      - Deployment Health Monitoring
      - Pod Restart Tracking
      - Pod Age Monitoring
      - Event Monitoring
      - GitHub Actions
      - ArgoCD GitOps Deployment
2. Architecture Overview
   2.0 Whole architecture
   2.1 Infrastructure Diagram
   2.2 Technology Stack
3. Dashboard Overview
   3.1 Dashboard Summary (Whole Dashboard)
   3.2 Explanation of each panel with picture (explanation about PromQL)
4. Project Implementation
   4.1 Local Environment
     4.1.1 Kind
     4.1.2 Docker Kubernetes
     4.1.3 Docker Desktop Kubernetes
   4.2 Monitoring Stack
     4.2.1 Prometheus
     4.2.2 Grafana
   4.3 CI/CD
     4.3.1 GitHub Actions
     4.3.2 GHCR
     4.3.3 ArgoCD
   4.4 Custom Exporter
     4.4.1 Explanation about metrics
5. Troubleshooting
   5.1 RBAC Permission Denied
   5.2 Prometheus Target Down (503)
   5.3 GHCR TLS Issue
   5.4 Grafana Duplicate Metrics
### Infos in Troubleshooting
1. ArgoCD Sync Status Unknown
Issue: Sync: Unknown
Cause: Syntax error in jqPathExpressions
  > original: .asd/asd/asd/asd
  > fixed: .asd.asd.asd.asd

2. Exporter Metrics No Appearing
Issue: Newly created metric is not showing in prometheus
Cause: Did not registered in Metric Registry

3. Prometheus Target Down
Issue: Prometheus Target Health is Down
Cause: Exporter did not have permission
  > Added permission in RBAC

4. Grafana Dashboard Duplicate Rows
Issue: Duplicated data were shown in Table Panel
Cause: The dashboard was using Range Query
   > Fixed: changed to Instant Query

5. Liveness/Readiness Probe Failed
Issue: HTTP probe failed with statuscode: 503 and kept creating events
Cause: Failed to call Kubernetes API in /readyz

6. GHCR Image Distribution in Kind Cluster
Issue: Kind Cluster could not pull GHCR Image
Cause: Internal TLS were blocking
   > Fixed: manually pull and pushed into Kind Cluster
     # docker pull "image name : image tag"
     # kind load docker-image "image name : image tag" --name "kind cluster name"

7. argocd admin password
Issue: could not login with decoded secret password
Cause: changed password in UI and the information is not updated in kubernetes
   > Fixed: recreated secret for admin account

###
6. Lessons Learned
7. Future Improvements



Key Features
- Setup
- Understanding
- Configuration
- Monitoring

Technic Overview
- 
- Docker
- Kubernetes
- Github Actions
- ArgoCD
- Prometheus
- Grafana
- Python




###############################################################
Scope of this week (Oct 19 ~ Oct 25)
1. Add metrics and create dashboard
   - Restart Pods (pod.status.container_statuses)
   - Old Pods (pod.metadata.creation_timestamp)
   - Kubernetes event Export (v1.list_event_for_all_namespaces())
2. Update README.MD
3. Finish the Project

Scope of this week (Oct 12 ~ Oct 18) - No need to continue.
1. Create Grafana Dashboard 1+ [Done]
2. Understand Python Custom Metric [Done]
3. Check ArgoCD Self-Heal [Done]
4. Create Alert + Discord 
5. Create at least 10 PromQL
   ex. sum by(namespace)....
       rate(......)
6. Add one more Python Metric
7. Play around with RBAC

---

## 2. `PERSONAL.md`

이건 회사에서 1주일 뒤에 다시 봤을 때 **"내가 어디까지 했고 다음에 뭘 해야 하지?"**가 바로 보이도록 간단하게 작성하는 게 좋겠습니다.

```markdown
# Personal DevOps Lab - Next Steps

## 현재까지 완료

2026년 9월 기준으로 여기까지 완료했다.

- Docker Desktop Kubernetes 환경 구성
- Python Kubernetes Exporter 작성
- Docker Image 생성
- Kubernetes Deployment 구성
- Service 구성
- ServiceAccount / RBAC 구성
- Kubernetes API 접근 확인
- Prometheus 설치
- Grafana 설치
- kube-prometheus-stack 설치
- ServiceMonitor 구성
- Prometheus Scraping 성공
- `k8s_pod_count` Metric 생성
- PromQL로 `k8s_pod_count = 19` 확인
- Prometheus retention 10d / 200MB 설정
- Docker 정리
- GitHub Repository 생성
- 프로젝트 첫 commit / push 완료

GitHub:

https://github.com/dandapss/DevOpsLab-k8s_monitoring

---

# 다음 작업

## 1. Grafana

가장 먼저 할 것.

- [ ] Grafana 접속
- [ ] Prometheus Data Source 확인
- [ ] `k8s_pod_count` 조회
- [ ] 첫 번째 Dashboard 생성
- [ ] Pod Count Panel 생성
- [ ] 가능하면 Kubernetes 관련 Panel 추가
>>> 이건 21/9에 완료

Prometheus PVC/PV
Grafana PVC/PV
Simple Grafana Dashboard
Simple Grafana Alert
Github Actions
> Docker Build
> GHCR Push
> GHCR를 private으로 구성하여 진행. (더 복잡)
> Self-hosted Runner (need to install)
> Auto Dpeloy

