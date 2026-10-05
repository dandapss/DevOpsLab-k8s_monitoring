# 프로젝트 1차 검토 로그 — 2026-10-05

## 요청과 작업 범위

- 개인 학습용 `k8s-monitoring` 저장소 전체 구성을 검토했다.
- `src/main.py`를 Kubernetes API 기반 리소스 exporter로 확장했다.
- 확장 수집에 필요한 차트 RBAC 권한과 Deployment 보안 설정을 반영했다.
- 삭제 작업이나 유료 서비스/비용 발생 작업은 수행하지 않았다.
- Kubernetes 클러스터에 명령을 실행하거나 Argo CD/Grafana를 설치·변경하지 않았다. 이번 작업은 저장소 파일 검토와 수정에 한정된다.

## 확인한 구성

- Python exporter: `src/main.py`
- 컨테이너: `Dockerfile`, `requirements.txt`
- Helm 차트: `kubernetes/Chart.yaml`, `kubernetes/values.yaml`, `kubernetes/templates/*`
- 실습 리소스: `kubernetes/temp_app.yaml`
- 모니터링 설정: `prometheus/values.yaml`, `grafana/values.yaml`
- 테스트/문서: `tests/test_main.py`, `README.md`, `PERSONAL.md`, `Troubleshoot.md`
- 작업 전 Git 상태는 `main...origin/main`으로 보였으며, 무시된 `.pytest_cache` 경로 접근 경고가 있었다.

## 반영한 변경

### `src/main.py`

- 기존 Pod/Node/Namespace 수집에 Deployment replica 상태, namespace별 Service 수, namespace별 ConfigMap 수를 추가했다.
- Pod를 namespace 및 phase별로 집계한다.
- Deployment의 desired/ready/available replica 수를 `namespace`, `deployment`, `state` 라벨로 노출한다.
- `/cluster`는 실제 수집 결과를 사람이 읽을 수 있는 요약으로 보여준다.
- `/metrics`는 Prometheus 메트릭을 노출하고, 지원하지 않는 경로는 404를 반환한다.
- `/healthz`는 프로세스 생존 상태, `/readyz`는 Kubernetes API 연결을 확인한다.
- API 호출에 5초 timeout을 설정하고, 조회 실패 시 내부 오류 내용을 공개하지 않고 503을 반환한다.
- `ThreadingHTTPServer`를 써서 scrape/health 요청이 서로 막히지 않게 했다.
- Gauge 갱신과 scrape 출력 생성은 lock으로 직렬화해 동시 scrape 중 값이 비워지거나 섞이지 않게 했다.
- In-cluster 설정을 우선하고, 없으면 로컬 kubeconfig를 사용하도록 했다.
- 메트릭은 Kubernetes API의 현재 상태에서 계산한다. `temp_app.yaml` 파일 내용을 직접 파싱하지 않는다. manifest는 희망 상태이고, API는 apply 이후의 실제 상태와 replica 진행 상황을 제공한다.
- Secret 리소스와 Secret 데이터는 조회하지 않는다. ConfigMap은 개수 집계를 위해 목록 API를 호출하지만 데이터 자체는 응답/메트릭에 쓰지 않는다.

### Helm 차트

- `kubernetes/templates/clusterrole.yaml`: Service 및 ConfigMap 목록 조회 권한을 추가했다. 기존 Pod/Node/Namespace/Deployment 읽기 권한은 유지한다. 변경/삭제 권한은 없다.
- `kubernetes/templates/deployment.yaml`: 비 root 사용자, read-only root filesystem, 권한 상승 금지, capability 전체 제거, RuntimeDefault seccomp, liveness/readiness probe, CPU/메모리 requests와 limits를 추가했다.

## 주요 평가 및 보완 권고

1. **메트릭 목적과 manifest 상태를 구분해야 한다.** 새 exporter는 `temp_app.yaml`에 적힌 수치를 직접 보여주는 게 아니라, apply된 뒤 Kubernetes가 보고하는 리소스를 센다. 아직 manifest를 적용하지 않았다면 해당 오브젝트 메트릭은 나타나지 않는다.
2. **ClusterRole은 전체 클러스터 범위다.** 모든 namespace의 Pod·Deployment·Service·ConfigMap을 나열할 수 있다. 개인 Docker Desktop 실습에는 편리하지만 운영 환경에서는 namespace 한정 Role/RoleBinding 또는 별도의 제한된 수집 설계를 권한다. ConfigMap에 민감정보를 넣지 않는 원칙도 지켜야 한다.
3. **`kubernetes/temp_app.yaml`에 Secret 샘플 값이 저장돼 있다.** Base64는 암호화가 아니며 값은 `test` / `test123`으로 디코딩된다. 실제 credential이 아니더라도 실습 manifest에 평문을 포함하는 습관은 피하고, 실제 비밀값이었다면 폐기/교체한 뒤 Git history에서도 제거해야 한다. 이번에는 사용자의 삭제 금지 지시에 따라 파일/히스토리를 변경하지 않았다.
4. **Image 태그가 `latest`다.** 재현 가능한 배포를 위해 릴리스 버전 또는 digest로 고정하고 배포 시 `imagePullPolicy`를 그 정책에 맞춰야 한다.
5. **Python 의존성이 고정되지 않았다.** `requirements.txt`의 Kubernetes 및 prometheus-client 버전을 lock/pin하면 빌드 재현성이 좋아진다. `pytest`가 런타임 이미지에 포함되는 현재 구성도 빌드 단계와 런타임 의존성 분리를 고려할 수 있다.
6. **테스트는 실질적으로 비어 있다.** `tests/test_main.py`의 현재 검증은 항상 성공하는 `assert True`뿐이다. API 응답 오류, Pod phase 집계, replica 수 계산과 HTTP 경로를 검증하는 mock 기반 테스트가 다음 개선점이다.
7. **CI 범위가 좁다.** 저장소의 GitHub Actions 테스트 workflow는 따로 검토 대상으로 확인됐으나 이번 변경에 맞춰 lint, 이미지 빌드, Helm template/lint 검증을 구성하면 좋다.
8. **Helm 라벨 선택은 환경 의존적이다.** ServiceMonitor의 `release: monitoring`은 Prometheus의 selector 설정과 설치 release 이름이 일치해야 한다. Prometheus에서 대상이 실제 `UP`인지 확인해야 한다.
9. **Grafana 및 Argo CD는 파일 검토만으로 동작 확인할 수 없다.** `grafana/values.yaml`은 persistence 일부만 설정한다. Dashboard provisioning, Alert rule, Contact point/notification policy 설정은 저장소에 보이지 않는다. 현재 클러스터의 Argo CD 설치/동작 여부와 Grafana datasource/alert 상태도 확인하지 않았다.
10. **권장 Dashboard 패널**: namespace별 Pod phase, Deployment desired/ready/available, namespace별 Deployment/Service/ConfigMap 개수, 전체 Node Ready 비율. 예시 PromQL은 아래와 같다.

```promql
sum by (namespace, phase) (k8s_pods)
k8s_deployment_replicas{state="ready"} / clamp_min(k8s_deployment_replicas{state="desired"}, 1)
sum by (namespace, resource) (k8s_namespace_resources)
k8s_nodes_ready / clamp_min(k8s_nodes_total, 1)
```

## 다음 진행 권장 순서

1. `temp_app.yaml`을 원하는 namespace에 적용하고 리소스 상태를 확인한다.
2. 수정된 exporter 이미지를 고유 버전으로 빌드해 Docker Desktop Kubernetes에서 사용할 수 있게 한다. 현재 Helm 기본 image는 GHCR `latest`이므로 로컬 이미지 사용 계획과 일치하는지 확인한다.
3. Helm template 결과를 확인한 뒤 upgrade/install하고 exporter의 `/readyz`, `/cluster`, `/metrics` 응답을 확인한다.
4. Prometheus Targets에서 ServiceMonitor 대상이 `UP`인지 확인하고 새 metric 이름/라벨로 Grafana dashboard 패널을 만든다.
5. Alert는 우선 `Pending` Deployment replica 또는 exporter scrape 실패처럼 의미가 명확한 규칙을 추가하고, notification route/contact point의 전달 시험까지 확인한다.
6. Argo CD는 설치 확인 뒤 저장소/Helm 앱 연결, sync 상태, drift/self-heal 의도 여부를 확인한다.
7. 2차 프로젝트를 시작하기 전 현재 프로젝트의 이미지 버전, 배포 절차, 대시보드/알림, README를 서로 일치시키고 완료 기준을 정리한다.

## 확인 한계

요청 범위에 맞춰 저장소를 읽고 코드를 수정했으며 Kubernetes에 배포하거나 실행 검증을 하지는 않았다. 테스트 실행, Docker image build/push, Helm 설치/업그레이드, Argo CD/Grafana 변경도 하지 않았다. 특히 신규 securityContext의 `runAsUser: 10001`과 read-only filesystem이 실제 이미지/클러스터 정책과 호환되는지 배포 후 확인이 필요하다.

## 2026-10-05 최근 수정분 재검토

- 현재 저장소 상태를 다시 확인했다. 시작 시점의 Git working tree는 clean이었다.
- `README.md`를 포트폴리오용 짧은 영어 문서로 다시 썼다. 현재 exporter 기능, Helm/RBAC, Prometheus/Grafana, Argo CD, 파일 구조와 로컬 workflow를 설명한다.
- `kubernetes/templates/deployment.yaml` readinessProbe를 `/healthz`에서 `/readyz`로 변경했다. `src/main.py`의 `/readyz`는 Kubernetes API 접근을 확인하므로 liveness의 `/healthz`와 목적이 구분된다. 수정 위치에 YAML 주석을 추가했다.
- 파일 삭제는 하지 않았다. `PERSONAL.md`는 완료 여부가 오래된 체크리스트와 복사된 차트 예제가 들어 있어 정리/보관 후보지만, 삭제 전 사용자 승인이 필요하다. `tests/test_main.py`는 현재 내용이 `assert True`뿐이나 workflow가 실행하므로 삭제보다 실제 테스트로 채우는 편이 낫다. `.pytest_cache`는 도구 권한 경고로 상세 확인하지 않았다.
- `.github/workflows/test.yaml`은 수동 실행 workflow이며 `packages: write`가 전체 workflow에 주어지고, Trivy `exit-code: '0'`이라 취약점이 있어도 실패하지 않는다. `tests/test_main.py`도 실질적인 기능 검증은 하지 않는다. 이를 바꾸지는 않았다.
- `argocd/helm-monitor.yaml`은 자동 sync의 `prune: true`를 사용한다. 추후 차트에서 리소스 manifest를 제거하면 Argo CD가 클러스터 리소스를 삭제할 수 있으므로, 관련 변경은 적용 전 sync preview/diff를 확인해야 한다. 설정은 변경하지 않았다.
- `kubernetes/temp_app.yaml`의 Base64 Secret 샘플 문제는 이전 검토와 동일하다. 파일이나 Git history를 삭제/수정하지 않았다.
- 코드 테스트, 이미지 build/push, Helm 렌더/배포, Argo CD/Grafana 런타임 상태 확인은 이번에도 하지 않았다. `git diff --check`만 수행했다.
