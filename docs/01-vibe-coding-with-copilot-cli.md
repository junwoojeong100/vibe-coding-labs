# 01. GitHub Copilot CLI로 vibe coding하기

이 실습의 핵심은 **직접 한 줄씩 코딩하는 것이 아니라, GitHub Copilot CLI에게 의도를 설명하고 코드를 생성·반복 개선**하는 것입니다.
이 문서에서는 모든 lab에서 공통으로 사용할 **vibe coding 워크플로우**와 **프롬프트 작성 규칙**을 익힙니다.

---

## 🎯 vibe coding이란?

> **vibe coding** = 구현 세부사항을 직접 타이핑하는 대신, *원하는 결과(의도)* 를 자연어로 설명하고
> AI가 생성한 코드를 **검토 → 실행 → 피드백 → 반복**하며 완성해 가는 개발 방식.

핵심은 "코드를 받는 것"이 아니라 **"방향을 잡고 빠르게 반복하는 것"** 입니다. AI가 만든 코드를 항상 **읽고 이해한 뒤** 받아들이세요.

---

## 🔁 기본 루프

```
   ┌─────────────────────────────────────────────┐
   │ 1. 의도 설명 (프롬프트)                       │
   │ 2. Copilot CLI가 코드 생성/수정 제안          │
   │ 3. 제안 검토 (읽고 이해) → 승인/거절          │
   │ 4. 실행 & 결과 확인                            │
   │ 5. 부족하면 피드백 주고 반복                   │
   └─────────────────────────────────────────────┘
```

### Copilot CLI 시작하기

작업할 폴더(예: `lab01-single-agent/`)로 이동한 뒤 세션을 시작합니다.

```bash
cd lab01-single-agent
copilot
```

대화형 세션에서 프롬프트를 입력하면 Copilot CLI가 파일 생성·수정과 명령 실행을 제안합니다.
기본 권한 모드에서는 파일을 바꾸거나 명령을 실행하는 도구를 사용할 때 승인을 요청합니다.
세션 단위 허용, `/allow-all`, `--yolo`, autopilot 모드에서는 매번 묻지 않을 수 있으므로
`/diff`로 변경 내용을 직접 확인하세요.

> 한 번에 프롬프트만 실행하고 싶다면: `copilot -p "여기에 프롬프트"` 형태도 사용할 수 있습니다.

---

## ✍️ 좋은 프롬프트 작성 규칙

각 lab은 시작용 프롬프트를 제공합니다. 다음 요소를 갖추면 결과 품질이 크게 올라갑니다.

1. **목표(What)**: 무엇을 만들고 싶은가 — "MAF로 단일 Researcher agent를 만들어줘"
2. **제약(Constraints)**: 사용할 라이브러리·언어·파일명 — "Python, `agent_framework.foundry.FoundryChatClient` 사용, `agent.py`에 작성"
3. **입출력(I/O)**: 입력과 기대 출력 — "주제를 인자로 받아 핵심 사실 5가지를 출력"
4. **인증/설정**: "환경 변수 `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME` 사용, `DefaultAzureCredential`로 인증, `.env`는 `load_dotenv()`로 로드"
5. **검증(Done)**: "실행하면 결과가 콘솔에 출력되어야 함"

### 예시 (Lab 1 시작 프롬프트)

```
MAF(Microsoft Agent Framework, Python)로 단일 "Researcher" agent를 만들어줘.
- agent.py 파일에 작성
- agent_framework.foundry.FoundryChatClient + DefaultAzureCredential 사용
- 환경 변수 FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_MODEL_DEPLOYMENT_NAME 사용 (.env는 load_dotenv로 로드)
- 명령행 인자로 받은 주제에 대해 핵심 사실 5가지를 조사해 콘솔에 출력
- asyncio로 비동기 실행
```

---

## 🔍 생성된 코드 검토 체크리스트

승인 전에 항상 아래를 확인하세요. (각 lab의 `solution/`에 정답 코드가 있으니 비교해도 좋습니다.)

- [ ] **import가 정확한가?** — `from agent_framework.foundry import FoundryChatClient`, `from agent_framework.orchestrations import SequentialBuilder` 등
- [ ] **인증이 올바른가?** — `DefaultAzureCredential()` 사용, 하드코딩된 키/시크릿이 없는가?
- [ ] **환경 변수 이름이 규칙과 같은가?** — `FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- [ ] **비동기 처리** — `await agent.run(...)`, `asyncio.run(main())`
- [ ] **시크릿이 코드/커밋에 포함되지 않는가?**

Copilot CLI의 `/review`로 현재 변경분을 다시 검토하거나,
`.github/prompts/review-code.prompt.md`의 체크리스트를 `@`로 참조해 리뷰를 요청할 수 있습니다.

---

## 💡 막혔을 때 팁

- **에러 메시지를 그대로 붙여넣기**: "다음 에러가 났어: <에러>. 원인과 수정 방법을 알려주고 코드를 고쳐줘."
- **작게 쪼개기**: 한 번에 큰 기능을 요청하기보다 단계적으로(클라이언트 → agent → 실행) 요청.
- **레퍼런스 코드 참고**: 각 lab `solution/` 폴더의 정답 코드와 비교해 차이를 좁히세요.
- **공식 문서 확인**: MAF는 빠르게 업데이트되므로 설치된 버전과 API가 다를 수 있습니다. [MAF 문서](https://learn.microsoft.com/agent-framework/) 참고.

---

준비가 되었으면 첫 번째 lab으로 이동하세요 → [Lab 1 — 단일 Agent](../lab01-single-agent/README.md)
