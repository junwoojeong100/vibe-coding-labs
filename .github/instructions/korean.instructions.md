---
applyTo: "**"
---

# 한국어 작성 컨벤션

## 언어 규칙

- 모든 응답, 주석, docstring, 사용자 메시지, 문서(README·가이드)는 **한국어**로 작성한다.
- 코드 내 변수명·함수명·클래스명은 **영어**를 사용한다.
- 기술 용어는 한국어로 쓰되, 통용되는 영문 용어는 괄호로 병기한다.
  - 예: 멀티 에이전트(multi-agent), 호스티드 에이전트(hosted agent)

## 주석 및 문서

- 코드 주석은 한국어로 간결하게, 꼭 필요한 곳에만 작성한다.
- 함수 docstring은 Google 스타일로 작성하며 설명/Args/Returns를 한국어로 쓴다.
- README·`docs/`·각 lab 가이드는 한국어로 작성한다.

## 예외 (영어 유지)

- **Git 커밋 메시지·PR 제목/본문**은 영어로 작성한다(`git-commit.instructions.md` 우선).
- 코드 식별자, SDK 클래스/메서드명, 환경변수 키(`FOUNDRY_PROJECT_ENDPOINT` 등)는 영어 그대로 둔다.
