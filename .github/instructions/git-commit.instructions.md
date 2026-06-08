---
applyTo: "**"
---

# Git 커밋 메시지 컨벤션

> 이 규칙은 한국어 작성 컨벤션(`korean.instructions.md`)보다 **우선 적용**됩니다.
> 커밋 메시지는 오픈소스 관례·도구 호환성을 위해 영어로 통일합니다.

## 언어

- 모든 커밋 메시지(제목·본문)는 **영어**로 작성한다.
- 코드 주석·docstring·README 등 나머지 문서는 한국어를 유지한다.

## 형식 (Conventional Commits)

- 형식: `type(scope): subject`
- 주요 `type`: `feat`(기능) · `fix`(버그) · `docs`(문서) · `refactor` · `test` · `chore` · `perf` · `style`

## 작성 규칙

- 제목은 **50자 이내**, **명령형 현재 시제**로 작성한다.
  - 좋은 예: `docs: clarify hosted agent region support`
  - 나쁜 예: `docs: clarified region` / `문서 수정`
- 제목 끝에 마침표를 붙이지 않는다.
- 본문이 필요하면 제목과 한 줄 띄우고 **72자 단위로 줄바꿈**하며 "무엇을/왜"를 설명한다.

## 트레일러 (항상 포함)

```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## 보안

- `.env` 등 시크릿 파일이 스테이징되지 않았는지 커밋 전에 확인한다(`.env.example`만 포함).
