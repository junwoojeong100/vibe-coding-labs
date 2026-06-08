"""Lab 1 — 단일 Researcher agent (Microsoft Agent Framework).

주어진 주제에 대해 핵심 사실 5가지를 조사해 콘솔에 출력합니다.

실행:
    python agent.py "양자 컴퓨팅"
    python agent.py "양자 컴퓨팅" --stream
"""

import asyncio
import os
import sys

from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# MAF는 .env를 자동으로 읽지 않으므로 직접 로드합니다.
load_dotenv()

RESEARCHER_INSTRUCTIONS = (
    "당신은 꼼꼼한 리서처입니다. 주어진 주제에 대해 신뢰할 수 있는 핵심 사실 5가지를 "
    "간결한 불릿(-)으로 정리하세요. 각 항목은 한 문장으로 작성하고, 과장이나 추측은 피합니다."
)


def build_researcher():
    """Foundry 채팅 클라이언트로 Researcher agent를 생성합니다."""
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )
    return client.as_agent(name="Researcher", instructions=RESEARCHER_INSTRUCTIONS)


async def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--stream"]
    stream = "--stream" in sys.argv
    topic = " ".join(args) or "Microsoft Agent Framework"

    researcher = build_researcher()
    prompt = f"다음 주제를 조사해줘: {topic}"

    print(f"🔎 주제: {topic}\n")

    if stream:
        # 스트리밍: 토큰이 생성되는 대로 출력
        async for update in researcher.run(prompt, stream=True):
            if update.text:
                print(update.text, end="", flush=True)
        print()
    else:
        # 비스트리밍: 완성된 응답을 한 번에 받음
        result = await researcher.run(prompt)
        print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
