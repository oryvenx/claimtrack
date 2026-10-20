from flask import request
from pydantic import BaseModel, ValidationError

from app.errors import ApiError


def parse_body(schema_cls: type[BaseModel]):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object", 400)
    try:
        return schema_cls.model_validate(data)
    except ValidationError as e:
        details = e.errors(include_url=False, include_context=False, include_input=False)
        raise ApiError("Validation failed", 400, details=details)