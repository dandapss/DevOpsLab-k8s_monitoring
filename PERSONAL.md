
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

---

# 2. Python Exporter 개선

현재 Metric:

```text
k8s_pod_count

추가로 어떤 Kubernetes 상태를 모니터링하면 좋은지 고민하면서 Metric 추가.

후보:

 Namespace별 Pod 수
 Pod 상태
 Pod Restart Count
 Deployment replica 상태
 Node 상태
 Job 상태

중요:

단순히 Metric을 많이 만드는 것이 목적이 아니다.

"운영자가 실제로 보고 싶은 정보가 무엇인가?"를 생각하면서 추가한다.
