
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

```
/// 9월 29일 추가 내용. helm을 이용한 k8s 구성. cluterrole 및 clusterrolebinding은 굳이 Release.Name을 쓸 필요는 없어보임.

### My Application Pod

# Chart.yaml
apiVersion: v2
name: helm_test
version: 1.0.0
appVersion: "1.0.0"


---
# values.yaml

replicaCount: 2

image:
  repository: ghcr.io/dandapss/custom-exporter
  tag: latest

app:
  label: k8s-resource-monitoring

container:
  port: 
    monitor: 8080
    service: 9090


---
### templates/

# Deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deploy
  namespace: {{ .Release.Namespace }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.app.label }}
  template:
    metadata:
      labels:
        app: {{ .Values.app.label }}
    spec:
      serviceAccountName: {{ .Release.Name }}-svcacc
      containers:
        - name: k8s-monitoring
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: {{ .Values.container.port.monitor }}		
			
			
---
### templates/

# ServiceAccount.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Release.Name }}-svcacc
  namespace: {{ .Release.Namespace }}
  
 
---
### templates/

# ClusterRole.yaml

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata: 
  name: {{ .Release.Name }}-crole
rules:
  - apiGroups: [""]
    resources: ["*"] # 여긴 Python App에서 무슨 정보를 긁어다 사용할지 확인해 보고 변경. 
    verbs: ["get", "list"]


---
### templates/

# ClusterRoleBinding.yaml

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: {{ .Release.Name }}-crolebinding
subjects:
- kind: ServiceAccount
  name: {{ .Release.Name }}-svcacc
  namespace: {{ .Release.Namespace }}
roleRef:
  kind: ClusterRole
  name: {{ .Release.Name }}-crole
  apiGroup: rbac.authorization.k8s.io


---
### templates/

# Service.yaml

apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-svc
  namespace: {{ .Release.Namespace }}
spec:
  type: ClusterIP
  selector:
    app: {{ .Values.app.label }}
  ports:
    - name: monitor
      port: {{ .Values.container.port.service }}	
      targetPort: {{ .Values.container.port.monitor }}	
