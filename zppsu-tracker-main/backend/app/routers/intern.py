from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import get_settings
from ..deps import sorted_desc, audit, distance_m, get_store, new_id, now, require_role, stamp

router = APIRouter(prefix="/api/intern", tags=["intern"])
intern_only = require_role("intern")


def _me(store, user: dict) -> dict:
    row = store.get("interns", user["id"])
    if not row:
        raise HTTPException(404, "OJT trainee record not found")
    return row


def _require_deployed(intern: dict) -> None:
    if intern["applicationStatus"] != "Approved" or not intern["orgId"]:
        raise HTTPException(403, "Your application has not been approved and deployed yet")


@router.get("/profile")
def profile(user: dict = Depends(intern_only), store=Depends(get_store)):
    intern = _me(store, user)
    return {
        "intern": intern,
        "organization": store.get("organizations", intern["orgId"]) if intern["orgId"] else None,
        "program": store.get("programs", intern["programId"]) if intern["programId"] else None,
        "locations": [l for l in store.list("locations", {"orgId": intern["orgId"]}) if l["status"] == "Active"]
        if intern["orgId"] else [],
    }


@router.get("/attendance")
def attendance(user: dict = Depends(intern_only), store=Depends(get_store)):
    return sorted_desc(store.list("attendance", {"internId": user["id"]}), "timestamp")


@router.get("/failed-attempts")
def failed_attempts(user: dict = Depends(intern_only), store=Depends(get_store)):
    return sorted_desc(store.list("failed_attempts", {"internId": user["id"]}), "timestamp")


class ClockIn(BaseModel):
    locationId: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    method: str = "Device biometrics"  # what the phone used to verify the person (Fingerprint / Face ID)


@router.post("/attendance", status_code=201)
def clock(body: ClockIn, user: dict = Depends(intern_only), store=Depends(get_store)):
    """Time In / Time Out. The server decides which one, and validates the geofence itself."""
    intern = _me(store, user)
    _require_deployed(intern)

    location = store.get("locations", body.locationId)
    if not location or location["orgId"] != intern["orgId"] or location["status"] != "Active":
        raise HTTPException(404, "Location not available for your organization")

    today = stamp().split(" ")[0]
    todays = [a for a in store.list("attendance", {"internId": user["id"]}) if a["date"] == today]
    time_in = next((a for a in todays if a["type"] == "Time In"), None)
    time_out = next((a for a in todays if a["type"] == "Time Out"), None)
    if time_out:
        raise HTTPException(409, "You have already completed today's attendance")
    kind = "Time Out" if time_in else "Time In"

    dist = distance_m(body.latitude, body.longitude, location["latitude"], location["longitude"])
    if dist > location["radius"]:
        reason = f"Outside allowed radius ({round(dist)}m from {location['name']}, limit {round(location['radius'])}m)"
        store.insert("failed_attempts", {
            "id": new_id("fail"), "internId": user["id"], "date": today, "timestamp": stamp(),
            "reason": reason, "stage": "GPS Validation",
        })
        audit(store, intern["name"], "Attendance verification failed", f"GPS Validation: {reason}", "Failed")
        raise HTTPException(422, reason)

    current = now()
    if kind == "Time In":
        hh, mm = (int(x) for x in get_settings().late_after.split(":"))
        status = "Late" if (current.hour, current.minute) > (hh, mm) else "On Time"
    else:
        status = "Completed"

    record = store.insert("attendance", {
        "id": new_id("att"), "internId": user["id"], "locationId": location["id"], "type": kind, "date": today,
        "timestamp": stamp(current), "status": status, "distance": round(dist),
        "faceVerified": True, "livenessVerified": True, "gpsVerified": True, "method": body.method,
    })

    if kind == "Time Out":
        started = datetime.strptime(time_in["timestamp"], "%Y-%m-%d %H:%M")
        worked = max(0.0, (current.replace(tzinfo=None) - started).total_seconds() / 3600)
        rendered = min(intern["requiredHours"], round((intern["renderedHours"] or 0) + worked, 1))
        patch = {"renderedHours": rendered}
        if rendered >= intern["requiredHours"]:
            patch["internshipStatus"] = "Completed"
        store.update("interns", intern["id"], patch)
    audit(store, intern["name"], f"Attendance {kind}", status)
    return record


@router.get("/daily-logs")
def daily_logs(user: dict = Depends(intern_only), store=Depends(get_store)):
    return sorted_desc(store.list("daily_logs", {"internId": user["id"]}), "date")


class LogIn(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    activities: str = Field(min_length=1)
    learnings: str = ""
    challenges: str = ""


@router.post("/daily-logs", status_code=201)
def submit_log(body: LogIn, user: dict = Depends(intern_only), store=Depends(get_store)):
    intern = _me(store, user)
    _require_deployed(intern)
    return store.insert("daily_logs", {
        "id": new_id("log"), "internId": user["id"], "date": body.date, "activities": body.activities,
        "learnings": body.learnings, "challenges": body.challenges, "status": "Pending",
        "reviewerComment": "", "reviewedAt": None,
    })


@router.get("/evaluations")
def evaluations(user: dict = Depends(intern_only), store=Depends(get_store)):
    released = [e for e in store.list("evaluations", {"internId": user["id"]}) if e["status"] == "Released"]
    return sorted_desc(released, "createdAt")


@router.get("/notifications")
def notifications(user: dict = Depends(intern_only), store=Depends(get_store)):
    return store.list("notifications", {"userId": user["id"]})


@router.post("/notifications/read")
def mark_read(user: dict = Depends(intern_only), store=Depends(get_store)):
    for n in store.list("notifications", {"userId": user["id"]}):
        if not n["read"]:
            store.update("notifications", n["id"], {"read": True})
    return {"ok": True}
