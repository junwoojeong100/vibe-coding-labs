# 99. 문제 해결 & 리소스 정리

실습 중 자주 만나는 문제·해결법과 비용을 막기 위한 정리 방법입니다.

---

## 🧪 로컬 실행 (Lab 1·2) 문제

| 증상 | 원인 / 해결 |
| --- | --- |
| `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'` | `.env`가 없거나 변수 미설정. `cp .env.example .env` 후 값을 채우고, 코드에 `load_dotenv()`가 있는지 확인. |
| `DefaultAzureCredential failed to retrieve a token` | 로그인 안 됨. `az login` 실행 후 `az account show`로 확인. 여러 구독이면 `az account set --subscription <id>`. |
| `ResourceNotFound` / `DeploymentNotFound` | `AZURE_AI_MODEL_DEPLOYMENT_NAME`이 실제 배포 이름과 다름. [Foundry 포털](https://ai.azure.com) → **Build → Deployments**에서 확인. |
| `ModuleNotFoundError: agent_framework...` | 가상환경 미활성/미설치. `.venv` 활성화 후 `pip install -r requirements.txt`. |
| `401` / `403` (권한) | 프로젝트에 대한 접근 권한 부족. **Foundry User** 이상 역할이 필요. |
| 모델 호출이 매우 느리거나 `429` | 모델 배포의 quota/TPM 부족. capacity를 늘리거나 다른 모델 사용. |
| Python 버전 오류 | 이 실습은 **Python 3.14.5** 기준. `python3 --version` 확인. |

---

## ☁️ 배포 (Lab 3) 문제

[hosted agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)의 공식 표를 기반으로 정리했습니다.

| 증상 | 해결 |
| --- | --- |
| `SubscriptionNotRegistered` | 리소스 공급자 등록: `az provider register --namespace Microsoft.CognitiveServices`. |
| provision 중 `AuthorizationFailed` | 구독/리소스 그룹에 **Contributor** 역할 요청. |
| `AuthenticationError` / `DefaultAzureCredential` 실패 | 자격증명 갱신: `azd auth logout` 후 `azd auth login`. |
| `AcrPullUnauthorized` | 프로젝트 managed identity에 Container Registry의 **AcrPull** 역할 부여. |
| 로컬 실행 시 `Connection refused` (8088) | 8088 포트를 쓰는 다른 프로세스 종료 후 재시도. |
| `azd ai agent init` 실패 | `azd version`이 1.25.3 이상인지 확인(`brew upgrade azd` / `winget upgrade Microsoft.Azd`). `azd extension list --installed`로 `azure.ai.agents` 확장 확인 후 `azd extension upgrade azure.ai.agents`. |
| `azd ai agent` 명령을 찾을 수 없음 | 확장 미설치. `azd extension install azure.ai.agents` (또는 `azd ai agent`를 한 번 실행하면 자동 설치). |
| Windows ARM64에서 `aiohttp`/`grpcio` 등 빌드 실패 | arm64 휠 부재. 로컬 실행(Step 3)을 건너뛰고 `azd deploy` 후 `azd ai agent invoke`로 원격 검증. |
| preview 패키지의 pip 의존성 경고 | **비차단(nonblocking)** 경고로, 무시해도 agent는 정상 동작합니다. |
| 트레이스가 Foundry/App Insights에 안 보임 | 전파에 **2~5분** 소요. 프로젝트에 App Insights가 **연결**됐는지 확인(Foundry 포털 → **Agents → Traces → Connect**). agent를 1회 이상 실행했는지 확인. hosted agent 트레이싱은 preview이며 `azd up` 배포 시 자동 연결됩니다. |

권한 매트릭스 전체는 [Hosted agent permissions reference](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions)를 참고하세요.

---

## 🧹 리소스 정리 (비용 주의)

Lab 3에서 배포하면 리소스 그룹에 Foundry 프로젝트·모델 배포·ACR·App Insights·Log Analytics·hosted agent가 생성되어 **과금**됩니다. 실습 후 반드시 정리하세요.

```bash
cd lab03-hosted-agent-deploy
azd down
```

- `azd down`은 삭제 대상 리소스를 나열하고 확인을 요청합니다. 정리에는 약 2~5분 소요됩니다.
- ⚠️ 해당 리소스 그룹의 **모든 리소스**가 영구 삭제됩니다. 다른 용도의 리소스가 같은 그룹에 있다면 함께 삭제되니 주의하세요.

Lab 1·2는 로컬 실행이라 별도 정리가 필요 없지만, 가상환경은 폴더의 `.venv`를 지우면 됩니다.

---

## 🔄 MAF 버전 관련 주의

Microsoft Agent Framework는 빠르게 업데이트되어, 공식 문서 예제와 설치된 패키지의 API(클래스명·임포트 경로)가 다를 수 있습니다.

- 설치된 버전 확인: `pip show agent-framework`
- 이 실습의 레퍼런스 코드는 **agent-framework 1.8.x** 기준으로 검증되었습니다.
- 임포트 오류가 나면 설치된 버전에 맞는 [MAF 문서](https://learn.microsoft.com/agent-framework/)를 확인하거나, Copilot CLI에 에러 메시지를 붙여 넣어 수정 방법을 물어보세요.

---

## 🆘 추가 도움

- [MAF 문서](https://learn.microsoft.com/agent-framework/)
- [Foundry Hosted Agents 문서](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
- [azd AI agent 확장](https://learn.microsoft.com/azure/developer/azure-developer-cli/extensions/azure-ai-foundry-extension)
- 막힐 때는 Copilot CLI에 **에러 메시지 전체**를 붙여 넣고 원인·수정안을 요청하세요.
