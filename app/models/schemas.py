from datetime import datetime
from enum import Enum
from app.models.database import db


class RequestStatus(Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    TIMEOUT = "timeout"


# HelpRequest model
class HelpRequest(db.Model):
    __tablename__ = "help_requests"

    id = db.Column(db.String(36), primary_key=True)
    customer_phone = db.Column(db.String(20), nullable=False)
    question = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=RequestStatus.PENDING.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    # Supervisor response
    supervisor_answer = db.Column(db.Text)
    supervisor_id = db.Column(db.String(50))

    # For follow-up
    follow_up_sent = db.Column(db.Boolean, default=False)
    follow_up_sent_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_phone": self.customer_phone,
            "question": self.question,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "supervisor_answer": self.supervisor_answer,
            "follow_up_sent": self.follow_up_sent,
        }


# KnowledgeBase model
class KnowledgeBase(db.Model):
    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50), default="supervisor")
    confidence = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    usage_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "source": self.source,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "usage_count": self.usage_count,
        }
