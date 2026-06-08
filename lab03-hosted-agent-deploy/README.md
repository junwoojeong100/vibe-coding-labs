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

> 🌐 **리전 주의**: hosted agent는 preview 단계라 일부 리전(예: **North Central US**)만 지원될 수 있습니다. `init` 중 리전을 선택할 때 [지원 리전](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)을 확인하세요.

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

### Step 6. 리소스 정리 (중요)

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

> Lab 2에서는 `output_from="all"`로 모든 단계를 출력했지만, 여기서는 hosted agent가 **최종 결과(Reviewer 출력)**만 반환하도록 `output_from`을 지정하지 않았습니다.

---

## 🎉 축하합니다!

세 개의 lab을 통해 다음을 완성했습니다.

- ✅ Copilot CLI vibe coding으로 MAF **단일 agent** 구현 (Lab 1)
- ✅ **멀티 agent workflow** 구성 (Lab 2)
- ✅ workflow를 **hosted agent로 배포·실행** (Lab 3)

문제가 있었다면 [문제 해결 & 정리 가이드](../docs/99-troubleshooting.md)를 확인하세요.
