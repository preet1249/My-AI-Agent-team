"""
Security utilities for webhooks and internal authentication
- HMAC SHA256 signature verification
- JWT creation and verification for internal calls
"""
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Header, Depends
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def verify_webhook_signature(
    payload: bytes,
    signature_header: str,
    secret: str = None
) -> bool:
    """
    Verify HMAC SHA256 webhook signature

    Args:
        payload: Raw request body as bytes
        signature_header: x-webhook-signature header value
        secret: Webhook secret (defaults to settings.WEBHOOK_SECRET)

    Returns:
        True if signature is valid

    Example:
        signature = "sha256=abc123..."
        valid = verify_webhook_signature(body, signature)
    """
    if not signature_header:
        logger.warning("Missing webhook signature header")
        return False

    if not signature_header.startswith('sha256='):
        logger.warning("Invalid signature format")
        return False

    secret = secret or settings.WEBHOOK_SECRET
    received_sig = signature_header.replace('sha256=', '')

    # Compute expected signature
    expected_sig = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    is_valid = hmac.compare_digest(received_sig, expected_sig)

    if not is_valid:
        logger.warning("Invalid webhook signature")

    return is_valid

def create_webhook_signature(payload: bytes, secret: str = None) -> str:
    """
    Create HMAC SHA256 signature for outgoing webhooks

    Args:
        payload: Request body as bytes
        secret: Webhook secret

    Returns:
        Signature header value (format: "sha256=<hex>")
    """
    secret = secret or settings.WEBHOOK_SECRET

    signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return f"sha256={signature}"

def create_internal_jwt(
    issuer: str = "orchestrator",
    audience: str = "worker",
    expires_in_seconds: int = 60,
    extra_claims: dict = None
) -> str:
    """
    Create JWT for internal agent-to-agent calls

    Args:
        issuer: Token issuer (who creates it)
        audience: Token audience (who receives it)
        expires_in_seconds: Token lifetime
        extra_claims: Additional claims to include

    Returns:
        JWT token string
    """
    now = datetime.utcnow()

    payload = {
        "iss": issuer,
        "aud": audience,
        "exp": now + timedelta(seconds=expires_in_seconds),
        "iat": now,
        "nbf": now  # Not valid before now
    }

    # Add extra claims if provided
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(
        payload,
        settings.INTERNAL_SIGNING_KEY,
        algorithm="HS256"
    )

    return token

def verify_internal_jwt(
    token: str,
    expected_audience: str = "worker"
) -> dict:
    """
    Verify internal JWT token

    Args:
        token: JWT token string
        expected_audience: Expected audience claim

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.INTERNAL_SIGNING_KEY,
            algorithms=["HS256"],
            audience=expected_audience,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True
            }
        )
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidAudienceError:
        logger.warning(f"Invalid JWT audience, expected: {expected_audience}")
        raise HTTPException(status_code=401, detail="Invalid token audience")

    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_internal_auth(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    FastAPI dependency for verifying internal authentication

    Usage:
        @router.post("/internal/agent-call")
        async def endpoint(auth: dict = Depends(verify_internal_auth)):
            # auth contains decoded JWT payload
            ...

    Args:
        authorization: Authorization header (Bearer <token>)

    Returns:
        Decoded JWT payload

    Raises:
        HTTPException: If auth is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Expected: Bearer <token>"
        )

    token = authorization.replace("Bearer ", "")
    return verify_internal_jwt(token)

def generate_external_id(prefix: str = "") -> str:
    """
    Generate unique external ID for idempotency

    Args:
        prefix: Optional prefix (e.g., "task", "email", "scrape")

    Returns:
        Unique ID string
    """
    import uuid
    from datetime import datetime

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique = str(uuid.uuid4())[:8]

    if prefix:
        return f"{prefix}-{timestamp}-{unique}"
    return f"{timestamp}-{unique}"
