from flask import Blueprint, render_template, request, jsonify
from app.models.schemas import HelpRequest, KnowledgeBase, db, RequestStatus

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def supervisor_dashboard():
    return render_template("dashboard.html")


@web_bp.route("/requests")
def requests_view():
    status = request.args.get("status", "pending")
    requests = (
        HelpRequest.query.filter(HelpRequest.status == status)
        .order_by(HelpRequest.created_at.desc())
        .all()
    )
    return render_template("requests.html", requests=requests, current_status=status)


@web_bp.route("/knowledge")
def knowledge_view():
    knowledge_entries = KnowledgeBase.query.order_by(
        KnowledgeBase.usage_count.desc()
    ).all()
    return render_template("knowledge.html", knowledge_entries=knowledge_entries)
