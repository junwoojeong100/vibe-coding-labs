# Vibe Coding Labs — 프로젝트 인스트럭션

GitHub Copilot CLI로 vibe coding하며 **Microsoft Agent Framework(MAF, Python)** agent를
만들고 **Microsoft Foundry Hosted Agents**로 배포하는 **한국어 단계별 실습 가이드**입니다.

> 공통 규칙(한국어·Python·Azure 인증·Git 커밋)은 `.github/instructions/`에서 관리한다.
> 이 파일에는 저장소 고유 규칙만 둔다.

## 저장소 구조

- `docs/` — 사전 준비(`00`)·vibe coding 입문(`01`)·문제 해결(`99`)
- `lab01-single-agent/` — 단일 Researcher agent
- `lab02-multi-agent-workflow/` — Researcher → Writer → Reviewer 순차 workflow
- `lab03-hosted-agent-deploy/` — 위 workflow를 Foundry hosted agent로 배포
- 각 lab = `README.md`(프롬프트·단계·검증) + `solution/`(정답 코드·`requirements.txt`·`.env.example`)

## 기술 스택 (검증 기준: MAF 구성 요소 1.8.0 / Python 3.14.5)

- **AI**: `agent-framework-core`·`agent-framework-openai`·`agent-framework-foundry` 1.8.0
- **Foundry**: `FoundryChatClient` (`agent_framework.foundry`)
- **오케스트레이션**: `SequentialBuilder` (`agent_framework.orchestrations`, 패키지 1.0.0rc3)
- **호스팅(Lab 3)**: `ResponsesHostServer` (`agent_framework_foundry_hosting`, 패키지 1.0.0a260604)
- **인증**: `DefaultAzureCredential`(`azure-identity`) — 로컬은 `az login` 세션
- **환경변수**: `python-dotenv`로 실행 폴더의 `.env` 로드

## 환경변수 (모든 lab 공통 — 이름 변경 금지)

- `FOUNDRY_PROJECT_ENDPOINT` — Foundry 프로젝트 엔드포인트
- `AZURE_AI_MODEL_DEPLOYMENT_NAME` — 배포한 모델 이름 (Lab 3의 `azure.yaml`이 hosted 환경에 같은 이름으로 매핑)

## 코드 패턴

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
result = await agent.run(prompt)                     # AgentResponse → result.text
async for update in agent.run(prompt, stream=True):  # 스트리밍 → update.text
    ...

# 멀티 agent (순차)
workflow = SequentialBuilder(participants=[a, b, c]).build()
result = await workflow.run(prompt)                  # result.get_outputs() → AgentResponse 목록(.messages)

# 호스팅 (Lab 3): workflow를 단일 agent로 감싸 노출
pipeline = workflow.as_agent(name="ContentPipeline")
ResponsesHostServer(pipeline).run()                  # http://localhost:8088/responses
```

## 핵심 제약

- agent/워크플로우 호출은 `async/await`, 콘솔 진입점은 `if __name__ == "__main__": asyncio.run(main())`.
  단, 호스팅 `main.py`는 `ResponsesHostServer(...).run()`을 호출하는 동기 `main()`이다.
- agent `instructions`·콘솔 출력·문서·주석은 한국어 (커밋 메시지만 영어).
- 엔드포인트·키 하드코딩 금지, `.env`에서 로드. `.env`는 커밋하지 않고 `.env.example`만 공유.
- 생성한 import/클래스명이 설치 버전과 다르면 설치된 버전 기준으로 검증한다(MAF는 빠르게 변경됨).
- 새 코드는 해당 lab `solution/`에 두고 위 패턴을 따른다. lab 간 환경변수·클라이언트 구성은 동일하게 유지한다.

## 배포 (Lab 3)

`azd ai agent` 확장(`azure.ai.agents` 1.0.0-beta.4+)으로 스캐폴드 →
리소스 준비(`azd provision`) → 로컬 테스트(`azd ai agent run`) →
배포(`azd deploy`) → 정리(`azd down`). 상세 단계는 `lab03-hosted-agent-deploy/README.md` 참조.
