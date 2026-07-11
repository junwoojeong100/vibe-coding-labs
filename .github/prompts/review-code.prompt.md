---
description: "이 저장소 규칙에 맞춰 코드를 리뷰하고 개선사항을 제안합니다"
mode: "agent"
---

# 코드 리뷰 요청

{{file_or_feature}} 코드를 아래 관점에서 검토하고 개선사항을 **한국어**로 알려주세요:

1. **패턴** — `FoundryChatClient` + `client.as_agent(...)`, 멀티 agent는 `SequentialBuilder(participants=[...])`, 호스팅은 `workflow.as_agent()` + `ResponsesHostServer(...)`를 따르는가?
2. **import 경로** — `agent_framework.foundry`·`agent_framework.orchestrations`·`agent_framework_foundry_hosting`이 검증된 requirements 기준으로 정확한가?
3. **비동기** — agent/워크플로우 호출이 `async/await`이고 진입점이 `asyncio.run(main())`인가?
4. **인증/환경변수** — `DefaultAzureCredential`을 쓰고 `FOUNDRY_PROJECT_ENDPOINT`/`AZURE_AI_MODEL_DEPLOYMENT_NAME`을 `.env`에서 로드(`load_dotenv()`)하는가?
5. **보안** — 엔드포인트·키 하드코딩, 시크릿 노출, `.env` 커밋 위험은 없는가?
6. **한국어 품질** — docstring·주석·사용자 메시지·agent `instructions`가 자연스러운가?

## 출력 형식

```
### ✅ 잘된 점
- ...

### ⚠️ 개선 제안
- [파일:줄번호] 설명

### 🔴 반드시 수정
- [파일:줄번호] 설명
```
