# 00. 사전 준비 (Prerequisites)

시작 전 아래 계정·도구·권한을 준비하고, 각 항목의 **확인 명령**으로 정상 설치를 검증하세요.

---

## 1. Azure 계정 및 Foundry 권한

| 항목 | 설명 |
| --- | --- |
| **Azure 구독** | 없으면 [무료 계정](https://azure.microsoft.com/free/)을 만드세요. |
| **Microsoft Foundry 프로젝트** | Lab 3에서 `azd`가 자동 생성할 수도 있고, 미리 만들어 둘 수도 있습니다([Foundry 포털](https://ai.azure.com)). |
| **모델 배포** | `gpt-4o`, `gpt-4.1`, `gpt-5` 계열 등 채팅 모델 1개. **배포 이름**을 그대로 `.env`에 사용합니다. Lab 1·2의 로컬 실행에도 필요합니다. |
| **Foundry Project Manager 역할** | hosted agent 생성·배포에 필요(프로젝트 범위). 구독에 **Owner** 또는 **User Access Administrator**가 있으면 나머지 역할 할당은 `azd`가 자동 처리합니다. |

> 💡 **Foundry Project Manager**는 이전의 *Azure AI Project Manager*와 동일합니다(역할 이름 변경).

---

## 2. 개발 도구

### 2.1 Python 3.14.5+

```bash
python3 --version    # Python 3.14.5 이상이어야 함
```

**Python 3.14.5** 기준으로 검증했습니다. 설치:
- macOS: `brew install python@3.14`
- 기타: [python.org 다운로드](https://www.python.org/downloads/)

> 참고: MAF·hosted agent의 공식 최소 요구 버전은 3.13이지만, 본 가이드는 **3.14.5**를 사용합니다. 더 낮은 버전은 설치/실행이 실패할 수 있습니다.

### 2.2 Git

```bash
git --version
```

### 2.3 Azure CLI (로컬 인증용)

Lab 1·2에서 `DefaultAzureCredential`이 사용할 로그인 자격증명을 제공합니다.

```bash
az version
az login          # 브라우저로 로그인
az account show   # 로그인된 구독 확인
```

설치: [Azure CLI 설치 가이드](https://learn.microsoft.com/cli/azure/install-azure-cli)

### 2.4 Azure Developer CLI (azd) 1.25.3+ — Lab 3 배포용

```bash
azd version       # 1.25.3 이상
```

설치: [azd 설치 가이드](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- macOS: `brew install azd` (또는 `brew upgrade azd`)
- Windows: `winget install Microsoft.Azd`

설치 후 **Foundry agents 확장**(`azd ai agent ...` 명령 제공)을 추가합니다(처음 실행 시 자동 설치되기도 함).

```bash
azd extension install azure.ai.agents
azd extension list --installed     # azure.ai.agents (Foundry agents) 가 보이면 OK
azd auth login                     # azd 용 Azure 로그인
```

> 이 확장(`azure.ai.agents`)은 **0.1.27-preview 이상**이 필요합니다. 확장 이름·버전은 preview 단계라 바뀔 수 있으니, 문제가 있으면 [공식 quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)를 확인하세요.

### 2.5 GitHub Copilot CLI — 이 실습의 핵심 도구

vibe coding으로 코드를 생성할 때 사용합니다. 활성 **GitHub Copilot 구독**이 필요합니다.

macOS/Linux는 Homebrew가 가장 간단합니다.

```bash
brew install copilot-cli             # macOS / Linux
copilot --version                    # 설치 확인
```

npm으로도 설치할 수 있습니다(모든 OS). 이때는 **Node.js 22 이상**이 필요합니다.

```bash
node --version                       # 22 이상
npm install -g @github/copilot
```

처음 실행하면 인증 절차가 진행됩니다.

```bash
copilot          # 대화형 세션 시작 → 안내에 따라 /login 으로 인증
```

자세한 내용: [GitHub Copilot CLI 문서](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli)

---

## 3. 공통 환경 변수

모든 lab은 동일한 두 개의 환경 변수를 사용합니다. Lab 3의 hosted 환경에서 자동 주입되는 이름과 맞췄습니다.

| 변수 | 예시 값 | 설명 |
| --- | --- | --- |
| `FOUNDRY_PROJECT_ENDPOINT` | `https://<account>.services.ai.azure.com/api/projects/<project>` | Foundry 프로젝트 엔드포인트 |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | `gpt-4o` | 배포한 모델 이름 |

각 lab `solution/`에 `.env.example`이 있습니다. **코드를 실행할 폴더에서** 복사해 본인 값으로 채우세요(`load_dotenv()`는 현재 폴더의 `.env`를 읽음).

```bash
cd lab01-single-agent/solution        # 정답 코드를 실행하는 경우
cp .env.example .env
# .env 파일을 열어 위 두 값을 채웁니다.
```

> 🔐 `.env` 파일에는 엔드포인트 등 민감 정보가 들어갈 수 있습니다. **절대 커밋하지 마세요**(루트 `.gitignore`에 이미 제외 처리됨).

엔드포인트·모델 이름은 [Foundry 포털](https://ai.azure.com)의 **Build → Deployments / Overview**에서 확인할 수 있습니다.

---

## 4. 준비 완료 체크리스트

- [ ] `az login` / `azd auth login` 으로 Azure에 로그인됨
- [ ] `python3 --version` ≥ 3.14.5
- [ ] `azd version` ≥ 1.25.3, `azd extension list --installed`에 `azure.ai.agents` 있음
- [ ] `copilot --version` 정상 출력, Copilot 인증 완료
- [ ] Foundry 프로젝트 엔드포인트와 모델 배포 이름 확보
- [ ] **Foundry Project Manager** 역할 보유

모두 준비되었다면 다음 문서로 이동하세요 → [01. Copilot CLI로 vibe coding하기](01-vibe-coding-with-copilot-cli.md)
