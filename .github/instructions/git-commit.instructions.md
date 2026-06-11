---
applyTo: "**"
---

# Git 커밋 메시지 컨벤션

> 이 규칙은 `korean.instructions.md`보다 **우선 적용**한다(커밋 메시지는 영어로 통일).

- 모든 커밋 메시지(제목·본문)는 **영어**로 작성한다. 나머지 문서·주석·docstring은 한국어를 유지한다.
- 형식은 Conventional Commits `type(scope): subject` — `feat`·`fix`·`docs`·`refactor`·`test`·`chore`·`perf`·`style`.
- 제목은 50자 이내, 명령형 현재 시제, 끝에 마침표 없음.
  - 좋은 예: `docs: clarify hosted agent region support` / 나쁜 예: `docs: clarified region`, `문서 수정`
- 본문이 필요하면 제목과 한 줄 띄우고 72자로 줄바꿈하며 "무엇을/왜"를 설명한다.
- 커밋 전 `.env` 등 시크릿이 스테이징되지 않았는지 확인한다(`.env.example`만 포함).

## 트레일러 (항상 포함)

```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```
