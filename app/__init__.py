from flask import Flask

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    if config:
        app.config.update(config)

    from app.routes.health import bp as health_bp

    app.register_blueprint(health_bp)

    return app