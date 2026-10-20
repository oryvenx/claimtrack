from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401  (registers tables with SQLAlchemy)
    from app.routes.health import bp as health_bp

    app.register_blueprint(health_bp)

    return app