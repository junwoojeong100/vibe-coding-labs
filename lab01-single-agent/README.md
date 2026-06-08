# Lab 1 — 단일 Agent (Researcher)

MAF(Microsoft Agent Framework)로 **첫 단일 agent**를 만듭니다. GitHub Copilot CLI로 vibe coding하며 코드를 생성하고, 로컬에서 실행해 봅니다.

| | |
| --- | --- |
| ⏱️ 난이도 | ⭐ 입문 |
| 🎯 결과물 | 주제를 입력하면 핵심 사실 5가지를 출력하는 **Researcher** agent |
| 📦 핵심 API | `FoundryChatClient`, `client.as_agent(...)`, `await agent.run(...)` |

> 시작 전 [00. 사전 준비](../docs/00-prerequisites.md)와 [01. vibe coding 입문](../docs/01-vibe-coding-with-copilot-cli.md)을 먼저 읽으세요.

---

## 📚 이 lab에서 배우는 것

- MAF의 **채팅 클라이언트**(`FoundryChatClient`)로 모델에 연결하는 법
- **agent 생성**(`instructions`로 역할 정의)과 **실행**(`run`)
- **스트리밍 vs 비스트리밍** 응답
- `DefaultAzureCredential` 기반 **passwordless 인증**과 `.env` 설정

---

## 🧭 진행 방식

각 단계는 **① Copilot CLI 프롬프트 → ② 검토 → ③ 실행** 순서입니다.
막히면 [`solution/`](solution/) 폴더의 정답 코드를 참고하세요.

> 🏃 **빠르게 결과만 보려면** 직접 작성하지 않고 제공된 정답을 바로 실행할 수 있습니다.
> ```bash
> cd lab01-single-agent/solution
> python3 -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt
> cp .env.example .env          # 본인 엔드포인트·모델 이름으로 채우기
> az login
> python agent.py "양자 컴퓨팅"
> ```
> 아래 Step들은 **직접 vibe coding**하는 흐름입니다. 이때 생성한 코드와 `.env`는 **실행할 폴더(예: lab 루트)에 함께** 두세요.

### Step 0. 작업 폴더와 가상환경 준비

```bash
cd lab01-single-agent
python3 -m venv .venv
source .venv/bin/activate          # Windows(PowerShell): .\.venv\Scripts\Activate.ps1
```

### Step 1. Copilot CLI로 agent 코드 생성

작업 폴더에서 Copilot CLI를 시작합니다.

```bash
copilot
```

아래 프롬프트를 입력하세요. (그대로 사용하거나 본인 표현으로 바꿔도 됩니다.)

```text
MAF(Microsoft Agent Framework, Python)로 단일 "Researcher" agent를 만들어줘.

요구사항:
- 파일명: agent.py
- agent_framework.foundry 의 FoundryChatClient 와 azure.identity 의 DefaultAzureCredential 사용
- 환경 변수 FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME 를 읽어서 클라이언트를 구성
- MAF는 .env를 자동 로드하지 않으므로 python-dotenv의 load_dotenv()를 호출
- client.as_agent(name="Researcher", instructions=...) 로 agent 생성
- instructions: 주어진 주제에 대해 신뢰할 수 있는 핵심 사실 5가지를 불릿으로 정리
- 명령행 인자로 받은 주제를 조사해 콘솔에 출력 (await agent.run 사용)
- asyncio.run(main())으로 비동기 실행
- requirements.txt 와 .env.example 도 함께 생성
```

> 💡 추가로 "응답을 스트리밍으로도 볼 수 있게 `--stream` 옵션을 넣어줘" 같이 반복 요청해 보세요.

### Step 2. 생성된 코드 검토

[vibe coding 입문 문서의 검토 체크리스트](../docs/01-vibe-coding-with-copilot-cli.md)로 확인합니다. 특히:

- `from agent_framework.foundry import FoundryChatClient` 임포트가 맞는지
- `DefaultAzureCredential()` 사용, 하드코딩된 키가 없는지
- 환경 변수 이름이 `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME` 인지

### Step 3. 의존성 설치 & 환경 변수 설정

```bash
pip install -r requirements.txt
cp .env.example .env
# .env 를 열어 본인의 엔드포인트와 모델 이름을 채웁니다.
az login            # DefaultAzureCredential이 사용할 자격증명
```

### Step 4. 실행

```bash
python agent.py "양자 컴퓨팅"
# 스트리밍으로 보기
python agent.py "양자 컴퓨팅" --stream
```

---

## ✅ 검증 (이렇게 나오면 성공)

```text
🔎 주제: 양자 컴퓨팅

- 양자 컴퓨팅은 큐비트를 이용해 0과 1을 동시에 표현하는 중첩 상태를 활용한다.
- ...
(핵심 사실 5개)
```

- 5개 내외의 사실이 불릿으로 출력되면 성공입니다.
- 인증/연결 오류가 나면 [문제 해결](../docs/99-troubleshooting.md)을 참고하세요.

---

## 🧠 핵심 개념 정리

| 개념 | 설명 |
| --- | --- |
| `FoundryChatClient` | Foundry 프로젝트의 모델에 연결하는 채팅 클라이언트 |
| `client.as_agent(...)` | 클라이언트로부터 `instructions`(역할)를 가진 agent 생성 |
| `await agent.run(prompt)` | agent 1회 실행, `AgentResponse` 반환 (`.text`로 텍스트 접근) |
| `agent.run(prompt, stream=True)` | 토큰 단위 스트리밍 (`async for update ...`, `update.text`) |
| `DefaultAzureCredential` | `az login` 등 환경의 자격증명을 자동 사용 (키 하드코딩 불필요) |

---

## ➡️ 다음 단계

단일 agent를 만들었으니, 이제 여러 agent를 연결해 봅니다.

**[Lab 2 — 멀티 Agent Workflow](../lab02-multi-agent-workflow/README.md)** 로 이동하세요.
