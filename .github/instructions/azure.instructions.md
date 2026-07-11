---
applyTo: "**/*.py"
---

# Azure 인증 / 시크릿 컨벤션

## 인증

- `DefaultAzureCredential`(`azure-identity`)을 사용한다 — 로컬은 `az login` 세션, Lab 3 hosted는 Managed Identity가 자동 적용된다(코드 변경 불필요).
- 인증 객체와 `FoundryChatClient`는 재사용하고 요청마다 새로 만들지 않는다.
- API 키 기반 대신 passwordless(`DefaultAzureCredential`)를 우선한다.

## 시크릿 / 보안

- 환경변수(`FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_MODEL_DEPLOYMENT_NAME`)는 `.env`에서 `load_dotenv()`로 로드하고 코드에 하드코딩하지 않는다. `.env`는 커밋 금지(`.env.example`만 공유).
- Lab 3 hosted 환경의 모델 이름은 `azure.yaml`의 `environmentVariables`로 같은 이름에 매핑한다. 플랫폼이 사용자 정의 변수 이름을 임의로 자동 주입한다고 설명하지 않는다.
- Lab 3 `azure.yaml`의 Responses container protocol은 `2.0.0`을 사용한다. deprecated된 `1.0.0`은
  `2.0.0`과 호환되지 않으므로 사용하지 않는다.
- 필수 환경변수는 `os.environ[...]`로 읽어 누락 시 즉시 실패시키거나 명확한 한국어 안내 후 종료한다.
- 로그·출력에 토큰·키 등 민감정보를 남기지 않는다.
