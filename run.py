from app import create_app
from app.models.database import db

app = create_app()


def initialize_database():
    """Initialize database tables and sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created!")

        # Initialize with sample data
        from app.agent.knowledge_base import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager()
        kb_manager.initialize_base_knowledge()
        print("Sample data initialized!")


if __name__ == "__main__":
    # Initialize database on startup
    initialize_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
