# Lab 3 — Hosted Agent로 배포·실행

Lab 2의 멀티 agent workflow를 **Microsoft Foundry Hosted Agent**로 배포해, 클라우드에서 호출 가능한 엔드포인트로 만듭니다.
`azd`로 스캐폴드한 hosted agent 프로젝트에 Copilot CLI로 우리의 파이프라인을 이식합니다.

| | |
| --- | --- |
| ⏱️ 난이도 | ⭐⭐⭐ 중급 |
| 🎯 결과물 | 조사→작성→검토 파이프라인을 수행하는 **배포된 hosted agent** |
| 📦 핵심 API/도구 | `workflow.as_agent()`, `ResponsesHostServer`, `azd ai agent ...`, `azd up` / `azd down` |

> [Lab 2](../lab02-multi-agent-workflow/README.md)를 먼저 완료하세요. 동일한 workflow를 재사용합니다.
> 또한 [사전 준비](../docs/00-prerequisites.md)에서 **azd + `azure.ai.agents` 확장 + Foundry Project Manager 역할**을 갖췄는지 확인하세요.

---

## 📚 이 lab에서 배우는 것

- workflow를 **단일 agent로 래핑**(`workflow.as_agent()`)해 호스팅하는 법
- `ResponsesHostServer`로 **Responses 프로토콜 HTTP 엔드포인트**(`:8088`) 노출
- `azd ai agent`로 hosted agent를 **스캐폴드 → 로컬 테스트 → 배포**하는 전체 흐름
- **Application Insights**로 트레이싱(관찰성)을 활성화하고 트레이스를 확인하는 법
- 배포 후 **playground**에서 테스트하고 **리소스를 정리**하는 법

---

## 🏗️ 배포 아키텍처

```
 main.py (ResponsesHostServer)
   └─ ContentPipeline = workflow.as_agent()
         └─ SequentialBuilder([Researcher, Writer, Reviewer])

 azd up
   ├─ provision: 리소스 그룹 · Foundry 프로젝트 · 모델 배포 · ACR · App Insights · Managed Identity
   └─ deploy:    컨테이너 빌드 → ACR push → Foundry Agent Service 배포
                       ▼
                Agent 엔드포인트 + playground
```

---

## 🧭 진행 방식

### Step 1. hosted agent 프로젝트 스캐폴드

기본 Agent Framework 샘플 manifest로 프로젝트 골격을 생성합니다. (대화형 프롬프트에서 Foundry 프로젝트/모델/리전 등을 선택)

```bash
cd lab03-hosted-agent-deploy
azd ai agent init -m "https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/responses/01-basic/agent.manifest.yaml"
```

> 🌐 **리전**: hosted agent는 **East US 2, Korea Central, Japan East, North Central US 등 여러 리전**에서 사용할 수 있습니다. 이 실습이 쓰는 **Responses 프로토콜**은 hosted agent를 지원하는 모든 리전에서 동작합니다. (참고: *Invocations(WebSocket)* 프로토콜만 현재 North Central US 전용입니다.) `init`에서 리전을 고를 때 [전체 지원 리전 목록](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents#region-availability)을 확인하세요.

생성되는 주요 파일:

| 파일 | 역할 |
| --- | --- |
| `main.py` | agent 호스트 진입점 (`ResponsesHostServer`) |
| `requirements.txt` | 의존성 |
| `azure.yaml` | `azd` 배포 정의(모델 배포 등 `config` 포함) |
| `agent.yaml` | 컨테이너 agent 사양(프로토콜·CPU/메모리·환경 변수) |
| `Dockerfile` | 컨테이너 이미지 정의 |

> 완료 메시지: **AI agent definition added to your azd project successfully!**

### Step 2. Copilot CLI로 파이프라인 이식 (vibe coding)

스캐폴드된 `main.py`는 **단일 기본 agent**를 호스팅합니다. 이를 Lab 2의 **멀티 agent 파이프라인**으로 바꿉니다.

```bash
copilot
```

```text
이 폴더의 main.py는 ResponsesHostServer로 단일 Agent를 호스팅하고 있어.
이걸 Researcher -> Writer -> Reviewer 순차 멀티 agent 파이프라인으로 바꿔줘.

요구사항:
- agent_framework.orchestrations 의 SequentialBuilder 로 3개 agent를 순차 연결
- 각 agent는 client.as_agent(name=..., instructions=..., default_options={"store": False}) 로 생성
  (Researcher: 핵심 사실 정리 / Writer: 초안 작성 / Reviewer: 검토·교정)
- 완성된 workflow를 workflow.as_agent(name="ContentPipeline", description=...) 로 감싸기
- 그 agent를 ResponsesHostServer(agent).run() 으로 호스팅
- 환경 변수는 기존대로 FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME 사용
- requirements.txt 에 agent-framework-foundry-hosting 이 있는지 확인하고 없으면 추가
```

> 막히면 [`solution/main.py`](solution/main.py)와 [`solution/requirements.txt`](solution/requirements.txt)를 참고하세요.

### Step 3. 로컬에서 테스트

`azd ai agent run`은 가상환경 생성·의존성 설치 후 `:8088`에서 agent를 띄웁니다.
(preview 패키지의 pip 경고는 무시해도 됩니다.)

```bash
azd ai agent run --no-inspector
```

다른 터미널에서 호출:

```bash
azd ai agent invoke --local "재택근무가 생산성에 미치는 영향에 대한 글을 써줘."
```

또는 `curl`로 직접 호출:

```bash
curl -sS -H "Content-Type: application/json" -X POST http://localhost:8088/responses \
  -d '{"input": "재택근무가 생산성에 미치는 영향에 대한 글을 써줘.", "stream": false}'
```

조사→작성→검토를 거친 최종 콘텐츠가 응답으로 오면 성공입니다.

> 💡 **정답 코드로 빠르게 로컬 확인**: `azd` 스캐폴드 없이 [`solution/`](solution/)을 직접 띄워볼 수도 있습니다.
> ```bash
> cd lab03-hosted-agent-deploy/solution
> python3 -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> cp .env.example .env          # 본인 엔드포인트·모델 이름으로 채우기
> az login
> python main.py                # http://localhost:8088/responses
> ```

### Step 4. Azure에 배포

provision(리소스 생성)과 deploy(컨테이너 빌드·배포)를 한 번에:

```bash
azd up
```

> 따로 실행하려면 `azd provision` 후 `azd deploy`. provision은 몇 분 걸립니다.

완료되면 **agent playground**와 **endpoint** 링크가 출력됩니다.

### Step 5. 배포 확인 & 호출

```bash
azd ai agent show                       # 상태가 Active 인지 확인
azd ai agent invoke "친환경 통근에 대한 짧은 글을 써줘."
azd ai agent monitor --follow           # (선택) 컨테이너 로그 스트리밍
```

**Foundry playground**에서도 테스트할 수 있습니다.
[Foundry 포털](https://ai.azure.com) → 프로젝트 선택 → **Build → Agents** → agent 선택 → **Open in playground**.

### Step 6. Application Insights로 트레이싱 활성화 & 확인

hosted agent의 동작(요청·모델 호출·단계별 지연·토큰 사용량·오류)을 OpenTelemetry 트레이스로 관찰합니다.

**App Insights 생성·연결 (트레이싱 활성화)** — 아래 두 경로 중 하나로 켭니다.

**방법 A — `azd`가 자동 처리 (이 실습 기본)**

`azd up`(또는 `azd provision`)이 Application Insights를 **자동 생성·연결**하고 컨테이너에
`APPLICATIONINSIGHTS_CONNECTION_STRING`을 주입합니다. 호스트(`ResponsesHostServer`)가 시작 시 OpenTelemetry를
자동 구성하므로 **추가 작업 없이 서버사이드 트레이싱이 켜집니다.** → 아래 *트레이싱 동작 검증*으로 이동.

**방법 B — Foundry 포털에서 직접 연결** (기존 App Insights 사용/수동 연결 시)

1. [ai.azure.com](https://ai.azure.com/?cid=learnDocs)에 로그인하고 우측 상단 **New Foundry** 토글을 켭니다.
2. 대상 **프로젝트**를 엽니다.
3. 좌측 내비게이션에서 **Agents**를 선택합니다.
4. 상단의 **Traces** 탭을 선택합니다.
5. 오른쪽 **Connect** 버튼을 클릭합니다.
   - **기존 리소스 연결**: 리소스를 선택 → **Connect**
   - **새로 만들기**: **Create new** 선택 → 마법사 완료
6. 연결 성공 메시지가 뜨면 트레이싱이 **자동 활성화**됩니다(코드 변경 없음, 수 분 내 반영).

> **Connect** 버튼이 안 보이면: 프로젝트 이름 메뉴 → **Project details** → **Connected resources** 탭 →
> **Add connection** → **Application Insights** 선택.

**(선택) App Insights 리소스를 CLI로 미리 생성**

```bash
az monitor app-insights component create \
  --app <appinsights-name> \
  --location <region> \
  --resource-group <resource-group> \
  --application-type web
```

생성한 리소스를 *방법 B*에서 선택해 연결합니다. (`application-insights` az 확장이 없으면 첫 실행 시 자동 설치됩니다.)

**권한**: 트레이스를 조회하려면 연결된 App Insights 리소스에 **Log Analytics Reader** 역할이 필요합니다
([역할 할당 방법](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-portal)).

> 참고: hosted agent 트레이싱은 현재 **preview**입니다(prompt agent는 GA). 트레이스에는 프롬프트·응답 등
> 민감정보가 포함될 수 있으니 접근 권한·보존 정책에 유의하세요.

**트레이싱 동작 검증**

1. 프로젝트가 App Insights에 연결됐는지 확인합니다.
2. agent를 **1회 이상 실행**합니다(`azd ai agent invoke "..."` 또는 playground).
3. Foundry 포털 **Agents → Traces**에서 새 트레이스가 보이는지 확인합니다(안 보이면 몇 분 뒤 새로고침).

**트레이스 보기 (3곳)**

- **Foundry 포털** → 프로젝트 → **Agents → Traces** 탭 (스팬 트리·지연·토큰, 최근 90일 검색/필터)
- **컨테이너 로그 스트리밍**: `azd ai agent monitor --follow`
- **Azure 포털** → 해당 Application Insights → **Investigate → Transaction search** 또는 **Performance**

**(선택) 로컬 실행에서도 트레이싱**

로컬(`python main.py`)에서 보낸 트레이스를 Azure Monitor로 내보내려면 MAF 내장 관찰성을 켭니다.
`build_pipeline_agent()`에서 client를 만든 직후 다음을 호출합니다(연결 문자열·리소스는 Foundry가 자동 설정):

```python
client.configure_azure_monitor()                       # 트레이스를 연결된 App Insights로 내보냄
# 프롬프트·응답 본문까지 포함하려면(민감정보 주의):
# client.configure_azure_monitor(enable_sensitive_data=True)
```

> `azure-monitor-opentelemetry` 패키지가 필요합니다(Lab 3 환경에는 이미 설치됨; 없으면 `pip install azure-monitor-opentelemetry`).

### Step 7. 리소스 정리 (중요)

과금을 막기 위해 실습이 끝나면 반드시 정리하세요.

```bash
azd down
```

> ⚠️ `azd down`은 리소스 그룹의 모든 리소스(Foundry 프로젝트·모델 배포·ACR·App Insights·hosted agent)를 **영구 삭제**합니다. 확인 후 진행됩니다.

---

## 🧠 핵심 개념 정리

| 개념 | 설명 |
| --- | --- |
| `workflow.as_agent(...)` | 멀티 agent workflow를 단일 agent(`WorkflowAgent`)처럼 호출 가능하게 래핑 |
| `ResponsesHostServer(agent)` | agent를 Responses 프로토콜 HTTP 서버(`:8088`)로 노출 |
| `agent.manifest.yaml` | `azd ai agent init`이 사용하는 agent 정의(이름·프로토콜·모델 리소스) |
| `azure.yaml` / `agent.yaml` | 배포 정의 / 컨테이너 사양(CPU·메모리·환경 변수) |
| `azd up` / `azd down` | 리소스 provision+deploy / 전체 삭제 |
| Application Insights / 트레이싱 | `azd`가 자동 생성·연결하고 호스트가 OTel을 자동 구성 → Foundry **Agents → Traces**에서 확인(preview). 로컬은 `client.configure_azure_monitor()` |

> Lab 2에서는 `output_from="all"`로 모든 단계를 출력했지만, 여기서는 hosted agent가 **최종 결과(Reviewer 출력)**만 반환하도록 `output_from`을 지정하지 않았습니다.

---

## 🎉 축하합니다!

세 개의 lab을 통해 다음을 완성했습니다.

- ✅ Copilot CLI vibe coding으로 MAF **단일 agent** 구현 (Lab 1)
- ✅ **멀티 agent workflow** 구성 (Lab 2)
- ✅ workflow를 **hosted agent로 배포·실행** (Lab 3)

문제가 있었다면 [문제 해결 & 정리 가이드](../docs/99-troubleshooting.md)를 확인하세요.
