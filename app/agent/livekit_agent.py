import asyncio
import uuid
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import ChatContext, ChatMessage
from livekit.agents.voice_assistant import VoiceAssistant
from app.models.schemas import HelpRequest, db, RequestStatus
from app.agent.knowledge_base import KnowledgeBaseManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SalonAIAgent:
    def __init__(self):
        self.kb_manager = KnowledgeBaseManager()
        self.assistant = None

    async def _process_user_input(self, text: str, participant: rtc.Participant) -> str:
        """Process user input and return response or escalate"""

        # Check knowledge base first
        answer = self.kb_manager.get_answer(text)

        if answer:
            return answer
        else:
            # Escalate to human supervisor
            help_request_id = self._create_help_request(text, participant)
            logger.info(f"Created help request {help_request_id} for question: {text}")

            # Simulate texting supervisor
            self._notify_supervisor(help_request_id, text)

            return "Let me check with my supervisor and get back to you."

    def _create_help_request(self, question: str, participant: rtc.Participant) -> str:
        """Create a new help request in database"""
        request_id = str(uuid.uuid4())

        # In real scenario, get from participant metadata
        customer_phone = f"participant_{participant.sid}"

        help_request = HelpRequest(
            id=request_id,
            customer_phone=customer_phone,
            question=question,
            status=RequestStatus.PENDING.value,
        )

        db.session.add(help_request)
        db.session.commit()

        return request_id

    def _notify_supervisor(self, request_id: str, question: str):
        """Simulate texting supervisor - in production would be Twilio/etc"""
        logger.info(f"SUPERVISOR NOTIFICATION: Help needed for request {request_id}")
        logger.info(f"QUESTION: {question}")
        logger.info(f"-> Please check the supervisor UI to respond")

    async def follow_up_customer(self, request_id: str, answer: str):
        """Follow up with customer after supervisor response"""
        help_request = HelpRequest.query.get(request_id)
        if help_request:
            # In production: Integrate with Twilio to send SMS
            logger.info(f"CUSTOMER FOLLOW-UP: Calling {help_request.customer_phone}")
            logger.info(f"ANSWER: {answer}")

            help_request.follow_up_sent = True
            help_request.follow_up_sent_at = datetime.utcnow()
            db.session.commit()


async def entrypoint(ctx: JobContext):
    logger.info("Starting Salon AI Agent")

    await ctx.connect()

    # Wait for first participant to join
    participant = await ctx.wait_for_participant()
    logger.info(f"Participant joined: {participant.identity}")

    # Initialize agent
    agent = SalonAIAgent()
    agent.kb_manager.initialize_base_knowledge()

    # Simple chat loop for demo
    @ctx.room.on("data_received")
    def on_data_received(data: str, participant: rtc.Participant):
        if participant.identity.startswith("agent"):
            return

        async def process():
            response = await agent._process_user_input(data, participant)
            # Send response back
            await ctx.room.local_participant.publish_data(
                response, topic="chat_response"
            )

        asyncio.create_task(process())


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
