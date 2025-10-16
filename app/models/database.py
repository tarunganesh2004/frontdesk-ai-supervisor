from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Initialize with some sample data
        from app.agent.knowledge_base import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager()
        kb_manager.initialize_base_knowledge()
