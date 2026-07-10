---
applyTo: "**/*.py"
---

# Python 코드 컨벤션

## 환경 / 실행

- **Python 3.14.5** 사용(실습 표준; MAF는 3.10+, hosted agent quickstart·코드 배포 런타임은 3.13+).
- 각 lab `solution/`에서 가상환경을 만들고 의존성을 설치한다:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate      # macOS/Linux (Windows: .venv\Scripts\Activate.ps1)
  pip install -r requirements.txt
  ```

## 의존성

- 의존성은 각 lab `solution/requirements.txt`에 명시한다.
- fresh install의 resolver 오류를 피하도록 `agent-framework-core`·`openai`·`foundry`를
  1.8.0으로 고정하고, 멀티 agent는 `agent-framework-orchestrations` 1.0.0rc3을 추가한다.
- Lab 3은 `agent-framework-foundry-hosting` 1.0.0a260604와 누락된 직접 의존성 `mcp`를
  추가한다. 검증 없이 최신 MAF 구성 요소를 섞거나 메타 패키지 `agent-framework`로 바꾸지 않는다.

## 코드 스타일

- 모듈 최상단에 한국어 모듈 docstring을 둔다.
- 함수는 Google 스타일 한국어 docstring(설명/Args/Returns; 자명한 헬퍼는 생략 가능)을 작성한다.
- 타입 힌트를 적극 활용한다.
- import 순서: 표준 라이브러리 → 서드파티 → 로컬(그룹 사이 빈 줄).
- 비동기 호출(`async/await`)·진입점(`asyncio.run(main())`)·`load_dotenv()` 규칙은 `copilot-instructions.md`「핵심 제약」을 따른다.
