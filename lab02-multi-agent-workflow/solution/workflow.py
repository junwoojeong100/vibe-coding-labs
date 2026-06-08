"""Lab 2 — 멀티 Agent Workflow: Researcher -> Writer -> Reviewer.

세 개의 전문 agent가 순차적으로 협업해 콘텐츠를 완성합니다.
- Researcher: 주제를 조사해 핵심 사실 정리
- Writer: 조사 내용을 바탕으로 초안 작성
- Reviewer: 초안을 검토/교정

실행:
    python workflow.py "재택근무의 생산성"
"""

import asyncio
import os
import sys
from typing import cast

from agent_framework import AgentResponse, Message
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# MAF는 .env를 자동으로 읽지 않으므로 직접 로드합니다.
load_dotenv()

RESEARCHER_INSTRUCTIONS = (
    "당신은 리서처입니다. 주어진 주제에 대해 신뢰할 수 있는 핵심 사실과 근거를 "
    "불릿(-)으로 5~7개 정리하세요. 다음 단계(작가)가 활용할 재료를 제공하는 것이 목표입니다."
)
WRITER_INSTRUCTIONS = (
    "당신은 작가입니다. 바로 앞 리서처가 정리한 사실을 바탕으로, 주제에 대한 "
    "3~4문단 분량의 명확하고 매력적인 초안을 한국어로 작성하세요."
)
REVIEWER_INSTRUCTIONS = (
    "당신은 꼼꼼한 편집자입니다. 바로 앞 작가의 초안을 검토하여 사실 정확성, 논리, "
    "가독성을 개선한 최종본을 제시하세요. 무엇을 왜 고쳤는지 한 줄 요약도 덧붙입니다."
)


def build_workflow():
    """Researcher -> Writer -> Reviewer 순차 workflow를 생성합니다."""
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    researcher = client.as_agent(name="Researcher", instructions=RESEARCHER_INSTRUCTIONS)
    writer = client.as_agent(name="Writer", instructions=WRITER_INSTRUCTIONS)
    reviewer = client.as_agent(name="Reviewer", instructions=REVIEWER_INSTRUCTIONS)

    # output_from="all" 로 각 단계(Researcher/Writer/Reviewer)의 출력을 모두 받습니다.
    return SequentialBuilder(
        participants=[researcher, writer, reviewer],
        output_from="all",
    ).build()


async def main() -> None:
    topic = " ".join(sys.argv[1:]) or "재택근무가 생산성에 미치는 영향"
    workflow = build_workflow()

    prompt = f"다음 주제로 콘텐츠를 작성해줘: {topic}"
    result = await workflow.run(prompt)

    # 공유 대화에 사용자 입력 + 각 agent의 메시지를 모아 단계별로 출력
    conversation: list[Message] = [Message(role="user", contents=[prompt])]
    for output in result.get_outputs():
        response = cast(AgentResponse, output)
        conversation.extend(response.messages)

    print("===== 콘텐츠 작성 파이프라인 결과 =====")
    for i, msg in enumerate(conversation, start=1):
        name = msg.author_name or ("assistant" if msg.role == "assistant" else "user")
        print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")


if __name__ == "__main__":
    asyncio.run(main())
