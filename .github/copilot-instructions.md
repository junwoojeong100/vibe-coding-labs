# Vibe Coding Labs — 프로젝트 인스트럭션

이 저장소는 **GitHub Copilot CLI로 vibe coding**하며 **Microsoft Agent Framework(MAF, Python)** 기반
agent를 만들고 **Microsoft Foundry Hosted Agents**로 배포하는 **한국어 단계별 실습 가이드**입니다.

> 공통 규칙(한국어 작성, Python, Azure 인증, Git 커밋)은 `.github/instructions/` 아래 파일에서 관리합니다.
> 이 파일에는 **이 저장소에만 해당하는 규칙**을 둡니다.

## 저장소 구조

- `docs/` — 사전 준비(`00`)·vibe coding 입문(`01`)·문제 해결(`99`) (모두 한국어)
- `lab01-single-agent/` — 단일 Researcher agent
- `lab02-multi-agent-workflow/` — Researcher → Writer → Reviewer 순차 workflow
- `lab03-hosted-agent-deploy/` — 위 workflow를 Foundry hosted agent로 배포
- 각 lab = `README.md`(Copilot CLI 프롬프트·단계·검증) + `solution/`(정답 코드 · `requirements.txt` · `.env.example`)

## 기술 스택 (검증 기준: `agent-framework` 1.8.0 / Python 3.13)

- **AI Framework**: Microsoft Agent Framework — 메타 패키지 `agent-framework` (foundry·orchestrations 포함)
- **Foundry 연동**: `FoundryChatClient` (`agent_framework.foundry`)
- **오케스트레이션**: `SequentialBuilder` (`agent_framework.orchestrations`)
- **호스팅(Lab 3)**: `ResponsesHostServer` (`agent_framework_foundry_hosting`)
- **인증**: `azure-identity` → `DefaultAzureCredential` (로컬은 `az login` 세션 사용)
- **환경변수**: `python-dotenv` → 코드를 실행하는 폴더의 `.env`

## 환경변수 (모든 lab 공통 — 이름 변경 금지)

- `FOUNDRY_PROJECT_ENDPOINT` — Foundry 프로젝트 엔드포인트
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` — 배포한 모델 이름
  - Lab 3 hosted 환경에서 **자동 주입**되는 이름과 동일하게 맞춘 것이므로 다른 이름을 쓰지 않는다.

## 코드 패턴 (생성/수정 시 이 패턴을 따른다)

```python
import os
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder          # 멀티 agent
from agent_framework_foundry_hosting import ResponsesHostServer       # Lab 3 호스팅
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()  # MAF는 .env를 자동 로드하지 않는다

client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    credential=DefaultAzureCredential(),
)

# 단일 agent
agent = client.as_agent(name="Researcher", instructions="...")
result = await agent.run(prompt)              # AgentResponse → result.text
async for update in agent.run(prompt, stream=True):  # 스트리밍 → update.text
    ...

# 멀티 agent (순차)
workflow = SequentialBuilder(participants=[a, b, c]).build()
result = await workflow.run(prompt)           # result.get_outputs() → AgentResponse 목록(.messages)

# 호스팅 (Lab 3): workflow를 단일 agent로 감싸 노출
pipeline = workflow.as_agent(name="ContentPipeline")
ResponsesHostServer(pipeline).run()           # http://localhost:8088/responses
```

### 핵심 제약 (항상 적용)

- 모든 agent/워크플로우 호출은 `async/await`. 콘솔 진입점은 `if __name__ == "__main__": asyncio.run(main())`
  (단, 호스팅 `main.py`는 `ResponsesHostServer(...).run()`을 호출하는 동기 `main()`).
- agent `instructions`·콘솔 출력·문서·주석은 **한국어**. (커밋 메시지만 영어 — `git-commit.instructions.md` 참조)
- 엔드포인트·키 등은 **하드코딩 금지**, `.env`에서 로드. `.env`는 커밋하지 않고 `.env.example`만 공유.
- MAF는 빠르게 업데이트되므로, 생성한 import/클래스명이 설치된 버전과 다르면 **설치된 버전 기준으로 검증**한다.
- 새 코드는 해당 lab의 `solution/`에 두고 위 패턴을 따른다. lab 간 환경변수·클라이언트 구성은 동일하게 유지한다.

## 배포 (Lab 3)

- `azd ai agent` 확장(**`azure.ai.agents`**)으로 스캐폴드 → 로컬 테스트(`azd ai agent run --no-inspector`) →
  배포(`azd up`) → 정리(`azd down`). 자세한 단계는 `lab03-hosted-agent-deploy/README.md` 참조.
