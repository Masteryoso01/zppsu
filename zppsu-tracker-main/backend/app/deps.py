import math
import uuid
from datetime import datetime
from functools import lru_cache
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings
from .security import decode_token
from .store import build_store

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def get_store():
    return build_store(get_settings())


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def now() -> datetime:
    return datetime.now(ZoneInfo(get_settings().timezone))


def stamp(dt: datetime | None = None) -> str:
    return (dt or now()).strftime("%Y-%m-%d %H:%M")


def sorted_desc(rows: list[dict], key: str) -> list[dict]:
    """Newest first. Timestamps only have minute precision, so ties fall back to insertion order (later = newer)."""
    indexed = sorted(enumerate(rows), key=lambda t: (t[1].get(key) or "", t[0]), reverse=True)
    return [r for _, r in indexed]


def audit(store, user: str, action: str, resource: str, result: str = "Success") -> None:
    store.insert("audit_logs", {
        "id": new_id("audit"), "user": user, "action": action, "resource": resource,
        "result": result, "timestamp": stamp(),
    })


def distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in metres."""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    if not creds:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = decode_token(creds.credentials)
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    return {"id": payload["sub"], "role": payload["role"], "name": payload["name"], "orgId": payload.get("orgId")}


def require_role(*roles: str):
    def dep(user: dict = Depends(current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(403, "You do not have access to this resource")
        return user

    return dep


def public_intern(row: dict) -> dict:
    return row  # interns rows hold no secrets; credentials live in the `users` table


def org_name(store, org_id: str | None) -> str | None:
    org = store.get("organizations", org_id) if org_id else None
    return org["name"] if org else None
