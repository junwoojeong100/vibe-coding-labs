---
applyTo: "**/*.py"
---

# Azure 인증 / 시크릿 컨벤션

## 인증

- 인증은 **`DefaultAzureCredential`**(`azure-identity`)을 사용한다.
  - 로컬에서는 `az login` 세션 자격증명을 자동으로 사용한다.
  - Lab 3 hosted 환경에서는 Managed Identity가 자동으로 사용된다(코드 변경 불필요).
- 인증 객체와 `FoundryChatClient`는 재사용하고, 요청마다 새로 만들지 않는다.

## 환경변수 / 시크릿

- 환경변수는 `.env`에 저장하고 `python-dotenv`의 `load_dotenv()`로 로드한다.
- `.env`는 `.gitignore`에 포함하여 **절대 커밋하지 않는다**. `.env.example`에 키 목록만 공유한다.
- 모든 lab 공통 환경변수(이름 고정):
  - `FOUNDRY_PROJECT_ENDPOINT`
  - `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- 엔드포인트·키 등 민감정보는 코드에 하드코딩하지 않는다.
- 필수 환경변수는 `os.environ[...]`로 읽어 누락 시 곧바로 실패하게 하거나, 명확한 한국어 안내 후 종료한다.

## 보안

- 로그·출력에 토큰·키 등 민감정보를 남기지 않는다.
- API 키 기반 인증 대신 `DefaultAzureCredential`(passwordless)을 우선한다.
