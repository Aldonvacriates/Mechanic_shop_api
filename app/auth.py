"""Token authentication helpers.

Why: centralizing JWT encode/decode and the `token_required` decorator keeps
auth behavior consistent across blueprints and avoids duplicating the secret
key logic in every route.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, jsonify, request


def encode_token(customer_id):
    """Return a signed JWT identifying a specific customer.

    Why: the token embeds the customer id so protected routes can recover the
    caller's identity without an extra DB lookup on every request.
    """

    payload = {
        "sub": str(customer_id),
        # Why: short-lived tokens limit damage if a token is leaked.
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    """Require a valid Bearer token on the decorated route.

    Why: routes that act on a single customer's data should never accept an
    arbitrary `customer_id` from the URL or body — the id must come from a
    signed token the server issued.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1].strip()

        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        # Why: forwarding the id (not the whole payload) keeps protected route
        # signatures small and predictable.
        customer_id = int(payload["sub"])
        return f(customer_id, *args, **kwargs)

    return decorated
