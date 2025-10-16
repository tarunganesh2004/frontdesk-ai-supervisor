import re
from datetime import datetime
from app.models.schemas import KnowledgeBase
from app.models.database import db


class KnowledgeBaseManager:
    def __init__(self):
        self.initial_knowledge = {
            "What are your hours?": "We're open Monday to Friday from 9 AM to 7 PM, and Saturday from 10 AM to 5 PM.",
            "Do you take walk-ins?": "Yes, we accept walk-ins based on availability, but we recommend booking an appointment to guarantee your spot.",
            "What services do you offer?": "We offer haircuts, coloring, styling, treatments, and special occasion styling.",
            "How much is a haircut?": "Our haircuts start at $45 for women and $35 for men.",
            "Do you have parking?": "Yes, we have complimentary valet parking for all our customers.",
        }

    def initialize_base_knowledge(self):
        """Initialize with basic salon knowledge"""
        print("Initializing knowledge base with sample data...")
        for question, answer in self.initial_knowledge.items():
            existing = KnowledgeBase.query.filter_by(question=question).first()
            if not existing:
                kb_entry = KnowledgeBase(
                    question=question, answer=answer, source="initial"
                )
                db.session.add(kb_entry)
        db.session.commit()
        print("Knowledge base initialized!")

    def get_answer(self, question: str):
        """Find the best matching answer for a question"""
        # First try exact match
        exact_match = KnowledgeBase.query.filter_by(question=question).first()
        if exact_match:
            exact_match.usage_count += 1
            exact_match.last_used = datetime.utcnow()
            db.session.commit()
            return exact_match.answer

        # Simple similarity matching - in production you'd use embeddings
        question_clean = self._clean_question(question)

        entries = KnowledgeBase.query.all()
        best_match = None
        best_score = 0

        for entry in entries:
            entry_question_clean = self._clean_question(entry.question)
            score = self._calculate_similarity(question_clean, entry_question_clean)

            if score > best_score and score > 0.6:  # Similarity threshold
                best_score = score
                best_match = entry

        if best_match:
            # Update usage stats
            best_match.usage_count += 1
            best_match.last_used = datetime.utcnow()
            db.session.commit()
            return best_match.answer

        return None

    def add_knowledge(self, question: str, answer: str, source: str = "supervisor"):
        """Add new knowledge to the base"""
        # Check if similar question already exists
        existing = self.get_answer(question)
        if not existing:
            kb_entry = KnowledgeBase(question=question, answer=answer, source=source)
            db.session.add(kb_entry)
            db.session.commit()
            print(f"Added new knowledge: {question}")

    def _clean_question(self, text: str) -> str:
        """Clean and normalize question text"""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity (for demo purposes)"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)
