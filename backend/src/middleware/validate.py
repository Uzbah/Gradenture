from functools import wraps
from flask import request, jsonify
from pydantic import ValidationError


def validate(schema_class):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                request.validated_data = schema_class(
                    **( request.get_json(force=True, silent=True) or {} )
                ).model_dump()
            except ValidationError as e:
                return jsonify({"errors": e.errors()}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
