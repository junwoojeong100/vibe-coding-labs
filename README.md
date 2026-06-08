# Vibe Coding Labs — GitHub Copilot CLI로 만드는 MAF Agent & Foundry 배포

GitHub Copilot CLI로 **vibe coding**(프롬프트 → 코드 생성 → 검토 → 반복)을 하면서,
**Microsoft Agent Framework(MAF, Python)** 기반의 **단일 agent**와 **멀티 agent workflow**를 직접 구현하고,
이를 **Microsoft Foundry Hosted Agents**로 배포·실행해 보는 단계별 실습 가이드입니다.

> 모든 lab은 **Copilot CLI에 넘길 프롬프트**를 제시합니다. 직접 생성하며 익히되, 막히면 각 lab의 `solution/` **레퍼런스 코드**를 참고하세요.

---

## 🎯 학습 목표

이 실습을 마치면 다음을 할 수 있습니다.

- GitHub Copilot CLI로 **vibe coding** 워크플로우를 활용해 agent 코드를 생성·반복 개선한다.
- MAF의 `Agent` 기본기(채팅 클라이언트, instructions, 실행/스트리밍)를 이해하고 **단일 agent**를 만든다.
- `SequentialBuilder`로 여러 agent를 연결해 **멀티 agent workflow**를 구성한다.
- workflow를 **Foundry Hosted Agent**로 래핑해 로컬 테스트 후 **`azd`로 배포·실행**한다.

---

## 🧩 시나리오: 콘텐츠 작성 파이프라인

주제를 입력하면 세 개의 전문 agent가 순차적으로 협업해 콘텐츠를 완성합니다.

```
[사용자 입력: 주제]
      │
      ▼
 Researcher ──► Writer ──► Reviewer ──► [최종 콘텐츠]
 (자료 조사)     (초안)      (검토/교정)
```

| 단계 | Agent | 역할 |
| --- | --- | --- |
| 1 | **Researcher** | 주제에 대한 핵심 사실·근거를 조사·정리 |
| 2 | **Writer** | 조사 내용을 바탕으로 초안 작성 |
| 3 | **Reviewer** | 초안을 검토·교정하여 최종본 완성 |

Lab을 진행하며 이 시나리오를 단계적으로 확장합니다.

| Lab | 내용 | 실행 위치 |
| --- | --- | --- |
| **Lab 1** | Researcher **단일 agent** | 로컬 콘솔 |
| **Lab 2** | Researcher → Writer → Reviewer **멀티 agent workflow** | 로컬 콘솔 |
| **Lab 3** | 위 workflow를 **hosted agent로 배포** | 로컬 → Foundry |

---

## 📚 실습 구성

먼저 사전 준비와 vibe coding 워크플로우 문서를 읽은 뒤, Lab 1 → 2 → 3 순서로 진행하세요.

1. [사전 준비 (`docs/00-prerequisites.md`)](docs/00-prerequisites.md) — Azure/Foundry, 도구 설치·인증
2. [Copilot CLI vibe coding 입문 (`docs/01-vibe-coding-with-copilot-cli.md`)](docs/01-vibe-coding-with-copilot-cli.md)
3. [Lab 1 — 단일 Agent](lab01-single-agent/README.md)
4. [Lab 2 — 멀티 Agent Workflow](lab02-multi-agent-workflow/README.md)
5. [Lab 3 — Hosted Agent 배포](lab03-hosted-agent-deploy/README.md)
6. [문제 해결 & 정리 (`docs/99-troubleshooting.md`)](docs/99-troubleshooting.md)

---

## ✅ 사전 준비 요약

자세한 내용과 설치 방법은 [`docs/00-prerequisites.md`](docs/00-prerequisites.md)를 참고하세요.

- **Azure 구독** + **Foundry 프로젝트**(모델 배포 포함) + **Foundry Project Manager** 역할
- **Python 3.13+**, **Git**
- **Azure Developer CLI(azd) 1.25.3+** 와 `azd ai agent` 확장(`azure.ai.agents`) **0.1.27-preview+**
- **GitHub Copilot CLI** (설치 및 인증 완료)
- `az login` 로그인 (DefaultAzureCredential 인증용)

---

## 🗂️ 저장소 구조

```
vibe-coding-labs/
├── README.md                         # (현재 문서) 전체 개요·학습 목표·Lab 인덱스
├── .gitignore                        # .env, .venv, __pycache__, .azure 등 제외
├── docs/
│   ├── 00-prerequisites.md           # 사전 준비/설치/인증
│   ├── 01-vibe-coding-with-copilot-cli.md  # Copilot CLI vibe coding 워크플로우
│   └── 99-troubleshooting.md         # 문제 해결 + 리소스 정리
├── lab01-single-agent/
│   ├── README.md
│   └── solution/                     # agent.py, requirements.txt, .env.example
├── lab02-multi-agent-workflow/
│   ├── README.md
│   └── solution/                     # workflow.py, requirements.txt, .env.example
└── lab03-hosted-agent-deploy/
    ├── README.md
    └── solution/                     # main.py, requirements.txt, .env.example
```

---

## 💰 비용 주의

Lab 3에서 Foundry에 배포하면 Azure 리소스가 생성되어 **과금**될 수 있습니다.
실습이 끝나면 반드시 [`docs/99-troubleshooting.md`](docs/99-troubleshooting.md)의 안내에 따라 **`azd down`**으로 리소스를 정리하세요.

---

## 🔗 참고 링크

- [Microsoft Agent Framework 개요](https://learn.microsoft.com/agent-framework/overview/)
- [첫 Agent 만들기 (Python)](https://learn.microsoft.com/agent-framework/get-started/your-first-agent)
- [Workflows](https://learn.microsoft.com/agent-framework/workflows/)
- [Foundry Hosted Agents (Python)](https://learn.microsoft.com/agent-framework/hosting/foundry-hosted-agent)
- [Hosted Agent Quickstart (azd)](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent)
- [GitHub Copilot CLI 문서](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli)
