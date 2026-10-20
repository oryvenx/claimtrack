from flask import Flask

from app.config import Config
from app.errors import register_error_handlers
from app.extensions import db, migrate


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401  (registers tables with SQLAlchemy)
    from app.routes.claims import bp as claims_bp
    from app.routes.health import bp as health_bp
    from app.routes.members import bp as members_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(claims_bp)

    register_error_handlers(app)

    return app