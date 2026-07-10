# Lab 3 — Hosted Agent로 배포·실행

Lab 2의 멀티 agent workflow를 **Microsoft Foundry Hosted Agent**로 배포해, 클라우드에서 호출 가능한 엔드포인트로 만듭니다.
`azd`로 스캐폴드한 hosted agent 프로젝트에 Copilot CLI로 우리의 파이프라인을 이식합니다.

| | |
| --- | --- |
| ⏱️ 난이도 | ⭐⭐⭐ 중급 |
| 🎯 결과물 | 조사→작성→검토 파이프라인을 수행하는 **배포된 hosted agent** |
| 📦 핵심 API/도구 | `workflow.as_agent()`, `ResponsesHostServer`, `azd ai agent ...`, `azd provision` / `azd deploy` / `azd down` |

> [Lab 2](../lab02-multi-agent-workflow/README.md)를 먼저 완료하세요. 동일한 workflow를 재사용합니다.
> 또한 [사전 준비](../docs/00-prerequisites.md)에서 **azd + `azure.ai.agents` 1.0.0-beta.4+ + 진행 방식에 맞는 Azure 역할**을 갖췄는지 확인하세요.
>
> 이 실습이 사용하는 hosted agent **직접 코드 배포**는 현재 preview입니다. 이 문서는 아래 핵심 의존성과
> `azure.ai.agents` 1.0.0-beta.5에서 검증한 절차입니다.

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

 azure.yaml
   └─ codeConfiguration: Python 3.14 / main.py / remote build

 azd provision
   └─ Foundry 프로젝트 · 모델 배포 · App Insights 등 지원 리소스

 azd deploy
   └─ 소스 ZIP 업로드 → Foundry 원격 빌드 → managed hosted container
                                               ▼
                                     Agent endpoint + playground
```

---

## 🧭 진행 방식

### Step 1. 도구 버전 확인

```bash
azd version                       # 1.25.3 이상
azd extension upgrade azure.ai.agents
azd ai agent version              # 1.0.0-beta.4 이상
az login
azd auth login
```

`az login`은 로컬 Python의 `DefaultAzureCredential`용이고, `azd auth login`은
provision/deploy 명령용입니다.

### Step 2. hosted agent 프로젝트 스캐폴드

기존 lab 파일과 생성물을 섞지 않도록 `.gitignore`에 등록된 `workspace/`에서 실행합니다.
Beta 확장의 원격 파일 다운로드 방식에 영향을 받지 않도록 공식 샘플의 필요한 폴더만
로컬로 받은 뒤 **`azure.yaml`** 경로를 전달합니다.

```bash
cd lab03-hosted-agent-deploy
mkdir -p workspace
cd workspace

git clone --depth 1 --filter=blob:none --sparse \
 https://github.com/microsoft-foundry/foundry-samples.git .foundry-samples
git -C .foundry-samples sparse-checkout set \
 samples/python/hosted-agents/agent-framework/responses/01-basic

azd ai agent init \
 -m ".foundry-samples/samples/python/hosted-agents/agent-framework/responses/01-basic/azure.yaml" \
 --deploy-mode code \
 --runtime python_3_14 \
 --entry-point main.py
```

> 이미 `.foundry-samples`가 있으면 두 `git` 명령은 건너뛰고 `azd ai agent init`부터 실행하세요.

대화형 프롬프트에서 agent 이름은 기본값 **`agent-framework-agent-basic-responses`**를
사용하고, 새 Foundry 프로젝트 또는 권한이 있는 기존 프로젝트, 리전, 모델 배포를 선택합니다.
완료 후 생성된 프로젝트로 이동합니다.

```bash
cd agent-framework-agent-basic-responses
```

> 🌐 **리전**: hosted agent는 **East US 2, Korea Central, Japan East, North Central US 등 여러 리전**에서 사용할 수 있습니다. 이 실습이 쓰는 **Responses 프로토콜**은 hosted agent를 지원하는 모든 리전에서 동작합니다. (참고: *Invocations(WebSocket)* 프로토콜만 현재 North Central US 전용입니다.) `init`에서 리전을 고를 때 [전체 지원 리전 목록](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents#region-availability)을 확인하세요.

생성되는 주요 파일:

| 파일 | 역할 |
| --- | --- |
| `azure.yaml` | 프로젝트·모델·agent·Responses 프로토콜·코드 배포 정의 |
| `src/agent-framework-agent-basic-responses/main.py` | agent 호스트 진입점 |
| `src/agent-framework-agent-basic-responses/requirements.txt` | 원격 빌드 의존성 |
| `src/agent-framework-agent-basic-responses/.env.example` | 로컬 직접 실행용 설정 예시 |
| `src/agent-framework-agent-basic-responses/Dockerfile` | 컨테이너 배포용 대안 파일. 이 실습의 `codeConfiguration` 경로에서는 사용하지 않음 |

> 완료 메시지: **AI agent definition added to your azd project successfully!**

`azure.yaml`의 구조를 확인합니다. 현재 샘플에는 최신 패키지용 protocol version이
`2.0.0`으로 생성될 수 있습니다. 이 가이드의 MAF 1.8.0 의존성 조합에서는 Step 3에서
공식 직접 코드 배포 문서의 Responses `1.0.0`으로 맞추며, 최종 형태는 다음과 같습니다.

```yaml
codeConfiguration:
 runtime: python_3_14
 entryPoint: main.py
protocols:
 - protocol: responses
   version: 1.0.0
environmentVariables:
 - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
   value: ${AZURE_AI_MODEL_DEPLOYMENT_NAME}
```

### Step 3. Copilot CLI로 파이프라인 이식 (vibe coding)

스캐폴드된 source의 `main.py`는 **단일 기본 agent**를 호스팅합니다. 이를 Lab 2의
**멀티 agent 파이프라인**으로 바꿉니다.

```bash
copilot
```

```text
src/agent-framework-agent-basic-responses/main.py의 단일 Agent를
Researcher -> Writer -> Reviewer 순차 멀티 agent 파이프라인으로 바꿔줘.

요구사항:
- agent_framework.orchestrations 의 SequentialBuilder 로 3개 agent를 순차 연결
- 각 agent는 client.as_agent(name=..., instructions=..., default_options={"store": False}) 로 생성
  (Researcher: 핵심 사실 정리 / Writer: 초안 작성 / Reviewer: 검토·교정)
- 완성된 workflow를 workflow.as_agent(name="ContentPipeline", description=...) 로 감싸기
- 그 agent를 ResponsesHostServer(agent).run() 으로 호스팅
- 환경 변수는 기존대로 FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME 사용
- azure.yaml의 Responses protocol version은 1.0.0으로 설정
- src/agent-framework-agent-basic-responses/requirements.txt에는 아래 검증 버전을 사용
  - agent-framework-core==1.8.0
  - agent-framework-openai==1.8.0
  - agent-framework-foundry==1.8.0
  - agent-framework-orchestrations==1.0.0rc3
  - agent-framework-foundry-hosting==1.0.0a260604
  - mcp>=1.24.0,<2.0.0
  - azure-identity>=1.25.0,<2.0.0
  - python-dotenv>=1.0.0,<2.0.0
```

> 막히면 [`solution/main.py`](solution/main.py)와 [`solution/requirements.txt`](solution/requirements.txt)를 참고하세요.

### Step 4. Azure 리소스 준비

**새 프로젝트를 선택했다면 이 단계 전에는 로컬 agent가 호출할 프로젝트 엔드포인트와 모델이
존재하지 않습니다.** 공식 샘플의 `azure.yaml`을 기준으로 리소스를 먼저 준비합니다.

```bash
azd provision
azd env get-values
```

기존 프로젝트를 선택한 경우에도 `azd provision`이 현재 환경과 필요한 연결을 확인·구성합니다.
리소스 생성과 모델 배포에는 시간이 걸리고 비용이 발생할 수 있습니다.

### Step 5. 로컬에서 테스트

`azd ai agent run`은 가상환경 생성·의존성 설치 후 `:8088`에서 agent를 띄웁니다.
프로젝트 루트에서 실행하고, 로그에 서버 준비 완료가 보일 때까지 기다립니다.

```bash
azd ai agent run
```

다른 터미널에서 호출:

```bash
curl -sS http://localhost:8088/readiness
# {"status":"healthy"}

azd ai agent invoke --local "재택근무가 생산성에 미치는 영향에 대한 글을 써줘."
```

또는 `curl`로 직접 호출:

```bash
curl -sS -H "Content-Type: application/json" -X POST http://localhost:8088/responses \
  -d '{"input": "재택근무가 생산성에 미치는 영향에 대한 글을 써줘.", "stream": false}'
```

조사→작성→검토를 거친 최종 콘텐츠가 응답으로 오면 성공입니다.

> `ExperimentalWarning`은 preview API 알림이지만, pip의 `ERROR`, 의존성 충돌,
> import 실패는 무시하지 마세요.
>
> `azure.ai.agents` 1.0.0-beta.5에서 로컬 client 창을 열지 않으려면 `--no-client`를
> 추가할 수 있습니다. 이전 preview의 `--no-inspector`와 이름이 다르므로 `--help`를 확인하세요.
>
> 테스트 후 첫 번째 터미널에서 `Ctrl+C`로 로컬 서버를 종료하세요.

> 💡 **정답 코드로 빠르게 로컬 확인**: `azd` 스캐폴드 없이 [`solution/`](solution/)을 직접 띄워볼 수도 있습니다.
> ```bash
> cd lab03-hosted-agent-deploy/solution
> python3 -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> cp .env.example .env          # 본인 엔드포인트·모델 이름으로 채우기
> az login
> python main.py                # http://localhost:8088/responses
> ```

### Step 6. Azure에 배포

```bash
azd deploy
```

`azure.yaml`에 `codeConfiguration`이 있으므로 source를 ZIP으로 업로드하고 Foundry가 원격으로
빌드합니다. 로컬 Docker 빌드나 직접 ACR push는 하지 않습니다.

완료되면 **agent playground**와 **endpoint** 링크가 출력됩니다.

> 처음부터 로컬 검증을 생략하고 provision+deploy를 한 번에 수행하려면 `azd up`도 사용할 수
> 있지만, 이 실습은 문제를 단계별로 분리하기 위해 `azd provision`과 `azd deploy`를 나눕니다.

### Step 7. 배포 확인 & 호출

```bash
azd ai agent show --output json         # status가 active인지 확인
azd ai agent invoke "친환경 통근에 대한 짧은 글을 써줘."
azd ai agent monitor --follow           # (선택) 직전 호출 session의 로그
```

**Foundry playground**에서도 테스트할 수 있습니다.
[Foundry 포털](https://ai.azure.com) → 프로젝트 선택 → **Build → Agents** → agent 선택 → **Open in playground**.

### Step 8. Application Insights 트레이싱 확인

hosted agent의 동작(요청·모델 호출·단계별 지연·토큰 사용량·오류)을 OpenTelemetry 트레이스로 관찰합니다.

공식 샘플의 `azd provision`이 Application Insights를 생성·연결하고 hosted container에
`APPLICATIONINSIGHTS_CONNECTION_STRING`을 주입합니다. 호스트(`ResponsesHostServer`)가 시작 시 OpenTelemetry를
자동 구성하므로 별도 코드 없이 hosted 실행의 서버사이드 트레이싱이 켜집니다.

1. 프로젝트가 App Insights에 연결됐는지 확인합니다.
2. agent를 **1회 이상 실행**합니다(`azd ai agent invoke "..."` 또는 playground).
3. Foundry 포털 **Agents → Traces**에서 새 트레이스가 보이는지 확인합니다(안 보이면 몇 분 뒤 새로고침).

- **Foundry 포털** → 프로젝트 → **Agents → Traces** (스팬 트리·지연·토큰)
- **컨테이너 로그 스트리밍**: `azd ai agent monitor --follow`
- **Azure 포털** → 해당 Application Insights → **Investigate → Transaction search** 또는 **Performance**

트레이스를 보는 사용자에게는 연결된 Log Analytics workspace의 **Log Analytics Reader**
역할이 필요합니다. Foundry 평가 기능이 telemetry를 읽는 구성에서는 프로젝트 managed
identity에 **Log Analytics Data Reader** 역할을 부여하는 것이 권장됩니다
([Hosted agent permissions reference](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions)).
보존 기간과 샘플링은 Application Insights 설정을 따릅니다.

> 일반 prompt/hosted agent 트레이싱은 GA이지만 workflow/external agent 관련 기능 일부는 preview입니다.
> 트레이스에는 프롬프트·응답 등 민감정보가 포함될 수 있으므로 접근 권한과 보존 정책에 유의하세요.
> 로컬 실행까지 Azure Monitor로 내보내려면 비동기 설정이 필요하므로, 검증되지 않은 동기 호출을
> 추가하지 말고 [MAF 관찰성 문서](https://learn.microsoft.com/agent-framework/agents/observability)를 따르세요.

### Step 9. 리소스 정리 (중요)

과금을 막기 위해 실습이 끝나면 반드시 정리하세요.

```bash
azd down
```

> ⚠️ `azd down`은 리소스 그룹의 모든 리소스(Foundry 프로젝트·모델 배포·App Insights·
> hosted agent, 구성에 따라 ACR 포함)를 **영구 삭제**합니다. 확인 후 진행됩니다.

---

## 🧠 핵심 개념 정리

| 개념 | 설명 |
| --- | --- |
| `workflow.as_agent(...)` | 멀티 agent workflow를 단일 agent(`WorkflowAgent`)처럼 호출 가능하게 래핑 |
| `ResponsesHostServer(agent)` | agent를 Responses 프로토콜 HTTP 서버(`:8088`)로 노출 |
| 샘플 `azure.yaml` | `azd ai agent init`이 읽는 프로젝트·모델·agent 정의 |
| `codeConfiguration` | Python 런타임·진입점·원격 빌드를 지정하는 직접 코드 배포 설정 |
| `environmentVariables` | 모델 배포 이름 같은 사용자 정의 값을 hosted 환경에 매핑 |
| `azd provision` / `azd deploy` | Azure 지원 리소스 준비 / 새 immutable agent 버전 배포 |
| `azd down` | 현재 azd 환경이 만든 리소스 그룹 삭제 |
| Application Insights / 트레이싱 | `azd`가 연결하고 protocol host가 OTel을 내보냄 → Foundry **Agents → Traces**에서 확인 |

> Lab 2에서는 `output_from="all"`로 모든 단계를 출력했지만, 여기서는 hosted agent가 **최종 결과(Reviewer 출력)**만 반환하도록 `output_from`을 지정하지 않았습니다.

---

## 🎉 축하합니다!

세 개의 lab을 통해 다음을 완성했습니다.

- ✅ Copilot CLI vibe coding으로 MAF **단일 agent** 구현 (Lab 1)
- ✅ **멀티 agent workflow** 구성 (Lab 2)
- ✅ workflow를 **hosted agent로 배포·실행** (Lab 3)

문제가 있었다면 [문제 해결 & 정리 가이드](../docs/99-troubleshooting.md)를 확인하세요.
