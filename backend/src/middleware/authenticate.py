import os
import json
import requests
import jwt
from functools import wraps, lru_cache
from flask import request, jsonify, g
from jwt.algorithms import ECAlgorithm


@lru_cache(maxsize=1)
def _get_jwks_keys() -> dict:
    url = f"{os.getenv('SUPABASE_URL')}/auth/v1/.well-known/jwks.json"
    resp = requests.get(url, timeout=5)
    keys = {}
    for key in resp.json().get("keys", []):
        keys[key["kid"]] = ECAlgorithm.from_jwk(json.dumps(key))
    return keys


def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            header = jwt.get_unverified_header(token)
            alg = header.get("alg", "HS256")

            if alg == "HS256":
                payload = jwt.decode(
                    token,
                    os.getenv("SUPABASE_JWT_SECRET"),
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
            else:
                keys = _get_jwks_keys()
                public_key = keys.get(header.get("kid"))
                if not public_key:
                    return jsonify({"error": "Invalid token"}), 401
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=["ES256"],
                    options={"verify_aud": False},
                )

            g.user = {
                "sub":           payload.get("sub"),
                "email":         payload.get("email"),
                "role":          payload.get("user_metadata", {}).get("role", "user"),
                "user_metadata": payload.get("user_metadata", {}),
            }
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated
