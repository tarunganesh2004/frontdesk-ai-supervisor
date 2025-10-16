from flask import Flask
from .models.database import db


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///salon_ai.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key"

    db.init_app(app)

    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from .models import schemas

        db.create_all()

        # Initialize with some sample data
        from .agent.knowledge_base import KnowledgeBaseManager

        kb_manager = KnowledgeBaseManager()
        kb_manager.initialize_base_knowledge()

    # Register blueprints
    from .routes.api import api_bp
    from .routes.web import web_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(web_bp)

    return app
