from flask import Blueprint, request, jsonify
from app.models.schemas import HelpRequest, KnowledgeBase, RequestStatus
from app.models.database import db
from app.agent.knowledge_base import KnowledgeBaseManager
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)
kb_manager = KnowledgeBaseManager()


@api_bp.route("/help-requests", methods=["GET"])
def get_help_requests():
    status_filter = request.args.get("status", "all")

    query = HelpRequest.query

    if status_filter != "all":
        query = query.filter(HelpRequest.status == status_filter)

    requests = query.order_by(HelpRequest.created_at.desc()).all()
    return jsonify([req.to_dict() for req in requests])


@api_bp.route("/help-requests/<request_id>", methods=["GET"])
def get_help_request(request_id):
    help_request = HelpRequest.query.get_or_404(request_id)
    return jsonify(help_request.to_dict())


@api_bp.route("/help-requests/<request_id>/respond", methods=["POST"])
def respond_to_request(request_id):
    data = request.get_json()
    answer = data.get("answer")
    supervisor_id = data.get("supervisor_id", "demo_supervisor")

    if not answer:
        return jsonify({"error": "Answer is required"}), 400

    help_request = HelpRequest.query.get_or_404(request_id)

    # Update help request
    help_request.supervisor_answer = answer
    help_request.supervisor_id = supervisor_id
    help_request.status = RequestStatus.RESOLVED.value
    help_request.resolved_at = datetime.utcnow()

    # Add to knowledge base
    kb_manager.add_knowledge(help_request.question, answer)

    # Simulate follow-up with customer
    logger.info(f"CUSTOMER FOLLOW-UP: Calling {help_request.customer_phone}")
    logger.info(f"ANSWER: {answer}")

    help_request.follow_up_sent = True
    help_request.follow_up_sent_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True, "message": "Response sent to customer"})


@api_bp.route("/knowledge-base", methods=["GET"])
def get_knowledge_base():
    entries = KnowledgeBase.query.order_by(KnowledgeBase.usage_count.desc()).all()
    return jsonify([entry.to_dict() for entry in entries])


@api_bp.route("/knowledge-base", methods=["POST"])
def add_knowledge():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")

    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400

    kb_manager.add_knowledge(question, answer, "manual")
    return jsonify({"success": True})


@api_bp.route("/simulate-call", methods=["POST"])
def simulate_call():
    """Simulate a phone call for testing"""
    data = request.get_json()
    question = data.get("question")
    customer_phone = data.get("customer_phone", f"simulated_{uuid.uuid4()}")

    # Check if we know the answer
    known_answer = kb_manager.get_answer(question)

    if known_answer:
        # Create resolved request
        request_id = str(uuid.uuid4())
        help_request = HelpRequest(
            id=request_id,
            customer_phone=customer_phone,
            question=question,
            status=RequestStatus.RESOLVED.value,
            supervisor_answer=known_answer,
            resolved_at=datetime.utcnow(),
            follow_up_sent=True,
            follow_up_sent_at=datetime.utcnow(),
        )
        db.session.add(help_request)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "escalated": False,
                "answer": known_answer,
                "request_id": request_id,
            }
        )
    else:
        # Create pending help request
        request_id = str(uuid.uuid4())
        help_request = HelpRequest(
            id=request_id,
            customer_phone=customer_phone,
            question=question,
            status=RequestStatus.PENDING.value,
        )
        db.session.add(help_request)
        db.session.commit()

        # Simulate supervisor notification
        logger.info(f"SUPERVISOR NOTIFICATION: Help needed for request {request_id}")
        logger.info(f"QUESTION: {question}")

        return jsonify(
            {
                "success": True,
                "escalated": True,
                "message": "Escalated to supervisor",
                "request_id": request_id,
            }
        )
