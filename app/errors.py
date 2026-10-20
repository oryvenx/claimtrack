from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(e: ApiError):
        body = {"error": e.message}
        if e.details:
            body["details"] = e.details
        return jsonify(body), e.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(e: HTTPException):
        # Covers 404, 405, etc. so they are JSON too, not HTML pages
        return jsonify(error=e.description), e.code