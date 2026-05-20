"""Token authentication helpers.

Why: centralizing JWT encode/decode and the auth decorators keeps token
behavior consistent across blueprints and avoids duplicating secret-key logic
in every route. Customer and mechanic tokens are distinguished by a `role`
claim so the same machinery can guard both kinds of resources.
"""

from datetime import datetime, timedelta, timezone
from functools import wraps

from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from flask import current_app, jsonify, request


def _encode(subject_id, role):
    """Build and sign a JWT carrying the subject id and its role.

    Why: a shared encoder keeps customer and mechanic tokens structurally
    identical except for the `role` claim, which is what the wrappers check.
    """

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject_id),
        "role": role,
        # Why: python-jose expects numeric (epoch) timestamps for time claims.
        "iat": int(now.timestamp()),
        # Why: short-lived tokens limit damage if a token is leaked.
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def encode_token(customer_id):
    """Return a signed customer JWT (role='customer')."""

    return _encode(customer_id, "customer")


def encode_mechanic_token(mechanic_id):
    """Return a signed mechanic JWT (role='mechanic').

    Why: mechanics need a token that is provably different from a customer's so
    staff-only routes can reject customer tokens even when they are valid.
    """

    return _encode(mechanic_id, "mechanic")


def _verify(required_role):
    """Decode the Bearer token and confirm it carries the required role.

    Returns (subject_id, None) on success or (None, error_response) on failure,
    so the wrappers can short-circuit with the right status code.
    """

    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Missing or invalid Authorization header"}), 401)

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
    except ExpiredSignatureError:
        return None, (jsonify({"error": "Token has expired"}), 401)
    except JWTError:
        return None, (jsonify({"error": "Invalid token"}), 401)

    # Why: a valid customer token must not unlock mechanic-only routes (and vice
    # versa), so the role claim is enforced, not just the signature.
    if payload.get("role") != required_role:
        return None, (jsonify({"error": "Insufficient permissions for this resource"}), 403)

    return int(payload["sub"]), None


def token_required(f):
    """Require a valid customer Bearer token on the decorated route.

    Why: routes that act on a single customer's data should never accept an
    arbitrary `customer_id` from the URL or body — the id must come from a
    signed token the server issued.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        customer_id, error = _verify("customer")
        if error:
            return error
        return f(customer_id, *args, **kwargs)

    return decorated


def mechanic_token_required(f):
    """Require a valid mechanic Bearer token on the decorated route.

    Why: shop-floor actions (managing inventory, adding parts to a ticket) are
    staff operations; this wrapper rejects customer tokens and hands the route
    the authenticated mechanic's id.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        mechanic_id, error = _verify("mechanic")
        if error:
            return error
        return f(mechanic_id, *args, **kwargs)

    return decorated
