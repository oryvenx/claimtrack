from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/health/db")
def health_db():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return jsonify(status="error", database="unreachable"), 503
    return jsonify(status="ok", database="reachable")