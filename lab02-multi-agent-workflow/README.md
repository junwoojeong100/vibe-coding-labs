# Lab 2 — 멀티 Agent Workflow (Researcher → Writer → Reviewer)

Lab 1의 단일 agent를 확장해, **여러 agent를 순차로 연결한 workflow**를 만듭니다.
콘텐츠 작성 파이프라인을 통해 MAF의 **오케스트레이션**을 익힙니다.

| | |
| --- | --- |
| ⏱️ 난이도 | ⭐⭐ 초급 |
| 🎯 결과물 | 주제 입력 → **조사 → 작성 → 검토** 3단계로 콘텐츠를 완성하는 workflow |
| 📦 핵심 API | `SequentialBuilder(participants=[...], output_from="all")`, `await workflow.run(...)`, `result.get_outputs()` |

> [Lab 1](../lab01-single-agent/README.md)을 먼저 완료하세요. 클라이언트/인증/환경 변수 설정이 동일합니다.

---

## 📚 이 lab에서 배우는 것

- 여러 agent를 **순차 workflow**로 연결하는 법(`SequentialBuilder`)
- agent 간 **공유 대화(conversation)**가 다음 단계로 전달되는 방식
- `output_from="all"`로 **각 단계의 출력**을 모두 확인하기
- workflow 실행 결과(`get_outputs()`)를 파싱해 단계별로 출력하기

---

## 🧩 파이프라인 구조

```
[주제]
   │
   ▼
 Researcher ──► Writer ──► Reviewer ──► [최종본]
 핵심 사실 정리   초안 작성    검토·교정

 ※ 각 agent는 앞 단계의 메시지를 포함한 "공유 대화"를 입력으로 받습니다.
```

---

## 🧭 진행 방식

> 🏃 **빠르게 결과만 보려면** 제공된 정답을 바로 실행할 수 있습니다.
> ```bash
> cd lab02-multi-agent-workflow/solution
> python3 -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> cp .env.example .env          # 본인 엔드포인트·모델 이름으로 채우기
> az login
> python workflow.py "재택근무가 생산성에 미치는 영향"
> ```
> 아래 Step들은 **직접 vibe coding**하는 흐름입니다. 생성한 코드와 `.env`는 **실행할 폴더에 함께** 두세요.

### Step 0. 작업 폴더와 가상환경 준비

```bash
cd lab02-multi-agent-workflow
python3 -m venv .venv
source .venv/bin/activate          # Windows(PowerShell): .\.venv\Scripts\Activate.ps1
```

### Step 1. Copilot CLI로 workflow 코드 생성

```bash
copilot
```

아래 프롬프트를 입력하세요.

```text
MAF(Microsoft Agent Framework, Python)로 순차 멀티 agent workflow를 만들어줘.

요구사항:
- 파일명: workflow.py
- 콘텐츠 작성 파이프라인: Researcher -> Writer -> Reviewer 3개 agent
  - Researcher: 주제의 핵심 사실 5~7개 정리
  - Writer: 리서처 결과로 3~4문단 초안 작성(한국어)
  - Reviewer: 초안을 검토/교정해 최종본 + 수정 요약 제시
- agent_framework.foundry 의 FoundryChatClient + DefaultAzureCredential 사용
- 환경 변수 FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME 사용, load_dotenv 호출
- agent_framework.orchestrations 의 SequentialBuilder 로 연결하고 output_from="all" 지정
- 명령행 인자로 받은 주제로 workflow.run 실행
- result.get_outputs() 를 순회하며 각 단계(agent)의 메시지를 단계별로 콘솔에 출력
- requirements.txt에는 아래 검증 버전을 사용
  - agent-framework-core==1.11.0
  - agent-framework-openai==1.10.1
  - agent-framework-foundry==1.10.1
  - agent-framework-orchestrations==1.0.0
  - azure-identity>=1.25.0,<2.0.0
  - python-dotenv>=1.0.0,<2.0.0
- requirements.txt 와 .env.example 도 함께 생성
```

### Step 2. 생성된 코드 검토

- `from agent_framework.orchestrations import SequentialBuilder` 임포트 확인
- `SequentialBuilder(participants=[researcher, writer, reviewer], output_from="all")` 형태인지
- `result.get_outputs()`로 각 `AgentResponse`의 `.messages`를 순회하는지

### Step 3. 의존성 설치 & 환경 변수 설정

```bash
pip install -r requirements.txt
cp .env.example .env      # 본인 값으로 채우기 (Lab 1과 동일)
az login
```

### Step 4. 실행

```bash
python workflow.py "재택근무가 생산성에 미치는 영향"
```

---

## ✅ 검증 (이렇게 나오면 성공)

```text
===== 콘텐츠 작성 파이프라인 결과 =====
------------------------------------------------------------
01 [user]
다음 주제로 콘텐츠를 작성해줘: 재택근무가 생산성에 미치는 영향
------------------------------------------------------------
02 [Researcher]
- ... (핵심 사실들)
------------------------------------------------------------
03 [Writer]
... (3~4문단 초안)
------------------------------------------------------------
04 [Reviewer]
... (검토·교정된 최종본 + 수정 요약)
```

user → Researcher → Writer → Reviewer 순서로 4개의 메시지가 보이면 성공입니다.

> ⚠️ Researcher에는 웹 검색 도구가 없으므로 결과는 실시간 조사가 아닙니다. Writer와 Reviewer가
> 같은 입력을 이어받아도 사실 검증이 자동으로 보장되지는 않습니다.

---

## 🧠 핵심 개념 정리

| 개념 | 설명 |
| --- | --- |
| `SequentialBuilder(participants=[...])` | agent들을 **순서대로** 연결하는 고수준 빌더 |
| 공유 대화 | 각 agent가 자신의 응답을 대화에 덧붙이고, 다음 agent가 그 전체를 입력으로 받음 |
| `output_from="all"` | 마지막 agent뿐 아니라 **모든 단계**의 출력을 결과로 반환 |
| `result.get_outputs()` | 실행 결과에서 출력 목록(`AgentResponse`)을 가져옴 (`.messages`로 접근) |

> 참고: `SequentialBuilder` 외에 그래프 기반 `WorkflowBuilder`(`add_edge`/`add_chain`)로도 동일한 순차 흐름을 만들 수 있습니다. 분기/병렬 등 복잡한 토폴로지가 필요하면 `WorkflowBuilder`를 사용하세요.

---

## ➡️ 다음 단계

이제 이 workflow를 **클라우드에 배포**해 누구나 호출할 수 있는 hosted agent로 만들어 봅니다.

**[Lab 3 — Hosted Agent 배포](../lab03-hosted-agent-deploy/README.md)** 로 이동하세요.
