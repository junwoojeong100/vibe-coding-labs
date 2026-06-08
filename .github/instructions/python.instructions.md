---
applyTo: "**/*.py"
---

# Python 코드 컨벤션

## 가상환경 / 실행

- **Python 3.14.5** 를 사용한다(이 실습 표준 버전; MAF·hosted agent 공식 최소 요구는 3.13).
- 각 lab의 `solution/`에서 가상환경을 만들고 의존성을 설치한다:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate      # macOS / Linux
  # .venv\Scripts\Activate.ps1   # Windows(PowerShell)
  pip install -r requirements.txt
  ```
- `.venv/`는 `.gitignore`에 포함되어 버전 관리에서 제외된다.

## 의존성 관리

- 의존성은 각 lab `solution/requirements.txt`에 명시한다.
- 핵심 패키지는 메타 패키지 **`agent-framework`**(foundry·orchestrations 포함)를 사용하고,
  Lab 3 호스팅은 **`agent-framework-foundry-hosting`**을 추가한다.
- SDK·핵심 패키지는 `>=x` 형태로 최소 버전을 명시해 재현성을 유지한다(프리릴리스 허용).

## 코드 스타일

- 모듈 최상단에 한국어 모듈 설명 docstring을 둔다.
- 함수에는 Args/Returns를 포함한 Google 스타일 한국어 docstring을 작성한다(자명한 헬퍼는 생략 가능).
- 타입 힌트를 적극 활용한다.
- import 순서: 표준 라이브러리 → 서드파티 → 로컬 모듈(그룹 사이 빈 줄).
- 모든 agent/워크플로우 호출은 `async/await`로 작성하고,
  콘솔 스크립트 진입점은 `if __name__ == "__main__": asyncio.run(main())` 형태를 따른다.
  (호스팅 `main.py`는 `ResponsesHostServer(...).run()`을 호출하는 동기 `main()`이다.)
- `.env`는 `load_dotenv()`로 로드한다(MAF는 자동 로드하지 않음).
- 사용자에게 보이는 오류는 한국어로 친절하게 출력한다.
