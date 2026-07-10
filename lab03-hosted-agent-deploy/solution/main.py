"""Lab 3 — Hosted Agent: 콘텐츠 작성 파이프라인을 Foundry hosted agent로 노출.

Lab 2의 Researcher -> Writer -> Reviewer workflow를 workflow.as_agent()로 감싸
ResponsesHostServer로 호스팅합니다. Foundry hosting 인프라가 :8088 에서 Responses
프로토콜 HTTP 엔드포인트를 제공합니다.

로컬 실행(권장):  azd ai agent run
직접 실행:        python main.py   (http://localhost:8088/responses)
"""

import os

from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import SequentialBuilder
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# 로컬 실행 시 .env 로드. hosted 환경에서는 azure.yaml 설정으로 변수를 주입합니다.
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

# 히스토리는 호스팅 인프라가 관리하므로 서비스 측 저장을 끕니다.
AGENT_OPTIONS = {"store": False}


def build_pipeline_agent():
    """Researcher -> Writer -> Reviewer workflow를 단일 agent로 감싸 반환합니다."""
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    researcher = client.as_agent(
        name="Researcher", instructions=RESEARCHER_INSTRUCTIONS, default_options=AGENT_OPTIONS
    )
    writer = client.as_agent(
        name="Writer", instructions=WRITER_INSTRUCTIONS, default_options=AGENT_OPTIONS
    )
    reviewer = client.as_agent(
        name="Reviewer", instructions=REVIEWER_INSTRUCTIONS, default_options=AGENT_OPTIONS
    )

    # output_from 미지정 → 마지막 단계(Reviewer)의 최종본을 응답으로 반환합니다.
    workflow = SequentialBuilder(participants=[researcher, writer, reviewer]).build()

    return workflow.as_agent(
        name="ContentPipeline",
        description="주제를 받아 조사→작성→검토 단계를 거쳐 콘텐츠를 생성하는 파이프라인 agent",
    )


def main() -> None:
    agent = build_pipeline_agent()
    server = ResponsesHostServer(agent)
    server.run()


if __name__ == "__main__":
    main()
