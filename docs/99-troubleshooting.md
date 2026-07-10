# 99. 문제 해결 & 리소스 정리

실습 중 자주 만나는 문제·해결법과 비용을 막기 위한 정리 방법입니다.

---

## 🧪 로컬 실행 (Lab 1·2) 문제

| 증상 | 원인 / 해결 |
| --- | --- |
| `KeyError: 'FOUNDRY_PROJECT_ENDPOINT'` | `.env`가 없거나 변수 미설정. `cp .env.example .env` 후 값을 채우고, 코드에 `load_dotenv()`가 있는지 확인. |
| `DefaultAzureCredential failed to retrieve a token` | 로컬 Python 인증은 `az login` 후 `az account show`로 확인. 여러 구독이면 `az account set --subscription <id>`. `azd` 명령 인증은 별도로 `azd auth login`이 필요합니다. |
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
| provision 중 `AuthorizationFailed` | 리소스 생성에는 **Contributor**, 역할 할당에는 **Owner** 또는 **Role Based Access Control Administrator**가 필요합니다. 이 quickstart는 리소스 그룹 범위 **Owner**가 가장 단순합니다. |
| `AuthenticationError` / `DefaultAzureCredential` 실패 | `azd` 작업이면 `azd auth logout` 후 `azd auth login`, 로컬 Python이면 `az login`을 다시 실행합니다. |
| `AcrPullUnauthorized` | 프로젝트 managed identity에 Container Registry의 **Container Registry Repository Reader**(권장) 또는 **AcrPull** 역할을 부여합니다. |
| 로컬 실행 시 `Connection refused` (8088) | 8088 포트를 쓰는 다른 프로세스 종료 후 재시도. |
| `azd ai agent init` 실패 | `azd version`이 1.25.3 이상인지 확인(`brew upgrade azd` / `winget upgrade Microsoft.Azd`). `azd extension upgrade azure.ai.agents` 후 `azd ai agent version`이 1.0.0-beta.4 이상인지 확인합니다. |
| `azd ai agent` 명령을 찾을 수 없음 | 확장 미설치. `azd extension install azure.ai.agents` (또는 `azd ai agent`를 한 번 실행하면 자동 설치). |
| 새 프로젝트 선택 후 로컬 호출이 실패 | 먼저 `azd provision`을 완료해야 프로젝트 엔드포인트와 모델 배포가 생깁니다. 그 뒤 `azd ai agent run`을 다시 실행합니다. |
| 샘플 clone 중 대상 폴더가 이미 존재 | `.foundry-samples`가 이미 있으면 clone과 sparse-checkout을 건너뛰고 기존 로컬 `azure.yaml`로 init합니다. 깨진 다운로드라면 `workspace/`를 새로 만든 뒤 다시 시작합니다. |
| `ResolutionImpossible` / `resolution-too-deep` | 각 `solution/requirements.txt`의 고정 버전을 그대로 사용합니다. `agent-framework` 메타 패키지나 최신 hosting 알파를 MAF 1.8.0 구성 요소와 임의로 섞지 마세요. |
| Windows ARM64에서 `aiohttp`/`grpcio` 등 빌드 실패 | arm64 휠 부재. 로컬 실행(Step 5)을 건너뛰고 `azd deploy` 후 `azd ai agent invoke`로 원격 검증. |
| `ExperimentalWarning` 출력 | 실습에서 사용하는 preview API 알림은 비차단 경고입니다. 반면 pip의 `ERROR`, 의존성 충돌, import 실패는 무시하지 마세요. |
| `LangChain instrumentation is disabled` 경고 | 이 실습은 LangChain을 사용하지 않으므로 정상입니다. 선택적 관찰성 연동이 비활성화됐다는 알림이며 agent 실행에는 영향이 없습니다. |
| 트레이스가 Foundry/App Insights에 안 보임 | 전파에 몇 분 걸릴 수 있습니다. 프로젝트와 App Insights 연결, agent 1회 이상 호출, 연결된 Log Analytics workspace의 조회 권한을 확인합니다. 보존·샘플링은 App Insights 설정을 따릅니다. |

권한 매트릭스 전체는 [Hosted agent permissions reference](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agent-permissions)를 참고하세요.

## 🧹 리소스 정리 (비용 주의)

Lab 3에서 배포하면 리소스 그룹에 Foundry 프로젝트·모델 배포·App Insights·Log Analytics·
hosted agent와 구성에 따라 ACR이 생성되어 **과금**됩니다. 실습 후 반드시 정리하세요.

```bash
cd lab03-hosted-agent-deploy/workspace/agent-framework-agent-basic-responses
azd down
```

- `azd down`은 삭제 대상 리소스를 나열하고 확인을 요청합니다. 정리에는 약 2~5분 소요됩니다.
- ⚠️ 해당 리소스 그룹의 **모든 리소스**가 영구 삭제됩니다. 다른 용도의 리소스가 같은 그룹에 있다면 함께 삭제되니 주의하세요.

Lab 1·2는 로컬 실행이라 별도 정리가 필요 없지만, 가상환경은 폴더의 `.venv`를 지우면 됩니다.

---

## 🔄 MAF 버전 관련 주의

Microsoft Agent Framework는 빠르게 업데이트되어, 공식 문서 예제와 설치된 패키지의 API(클래스명·임포트 경로)가 다를 수 있습니다.

- 설치된 버전 확인: `pip show agent-framework-core agent-framework-foundry agent-framework-orchestrations agent-framework-foundry-hosting`
- 이 실습의 레퍼런스 코드는 MAF core/openai/foundry **1.8.0**,
  orchestrations **1.0.0rc3**,
  **agent-framework-foundry-hosting 1.0.0a260604** 조합으로 검증되었습니다.
- 현재 `agent-framework` 메타 패키지는 fresh install에서 resolver 깊이 오류를 일으킬 수 있어
  필요한 구성 요소만 고정했습니다. hosting 1.0.0a260604가 선언하지 않은 `mcp`도 직접 명시합니다.
- 임포트 오류가 나면 설치된 버전에 맞는 [MAF 문서](https://learn.microsoft.com/agent-framework/)를 확인하거나, Copilot CLI에 에러 메시지를 붙여 넣어 수정 방법을 물어보세요.

---

## 🆘 추가 도움

- [MAF 문서](https://learn.microsoft.com/agent-framework/)
- [Foundry Hosted Agents 문서](https://learn.microsoft.com/azure/foundry/agents/concepts/hosted-agents)
- [azd AI agent 확장](https://learn.microsoft.com/azure/developer/azure-developer-cli/extensions/azure-ai-foundry-extension)
- 막힐 때는 Copilot CLI에 **에러 메시지 전체**를 붙여 넣고 원인·수정안을 요청하세요.
