from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..deps import sorted_desc, audit, get_store, new_id, require_role, stamp

router = APIRouter(prefix="/api/admin", tags=["admin"])
admin_only = require_role("admin")


def _org_interns(store, user: dict) -> list[dict]:
    return store.list("interns", {"orgId": user["orgId"]})


def _own_intern(store, user: dict, intern_id: str) -> dict:
    intern = store.get("interns", intern_id)
    if not intern or intern["orgId"] != user["orgId"]:
        raise HTTPException(404, "OJT trainee not found in your organization")
    return intern


@router.get("/dashboard")
def dashboard(user: dict = Depends(admin_only), store=Depends(get_store)):
    interns = _org_interns(store, user)
    ids = {i["id"] for i in interns}
    today = stamp().split(" ")[0]
    logs = [l for l in store.list("daily_logs") if l["internId"] in ids]
    return {
        "totalInterns": len(interns),
        "ongoing": sum(1 for i in interns if i["internshipStatus"] == "Ongoing"),
        "pendingLogs": sum(1 for l in logs if l["status"] == "Pending"),
        "todayAttendance": sum(1 for a in store.list("attendance") if a["internId"] in ids and a["date"] == today),
    }


@router.get("/interns")
def interns(user: dict = Depends(admin_only), store=Depends(get_store)):
    return _org_interns(store, user)


@router.get("/interns/{intern_id}")
def intern_detail(intern_id: str, user: dict = Depends(admin_only), store=Depends(get_store)):
    intern = _own_intern(store, user, intern_id)
    return {
        "intern": intern,
        "attendance": sorted_desc(store.list("attendance", {"internId": intern_id}), "timestamp"),
        "dailyLogs": sorted_desc(store.list("daily_logs", {"internId": intern_id}), "date"),
        "evaluations": sorted_desc(store.list("evaluations", {"internId": intern_id}), "createdAt"),
    }


@router.get("/attendance")
def attendance(user: dict = Depends(admin_only), store=Depends(get_store)):
    ids = {i["id"] for i in _org_interns(store, user)}
    return sorted_desc([a for a in store.list("attendance") if a["internId"] in ids], "timestamp")


@router.get("/failed-attempts")
def failed_attempts(user: dict = Depends(admin_only), store=Depends(get_store)):
    ids = {i["id"] for i in _org_interns(store, user)}
    return sorted_desc([f for f in store.list("failed_attempts") if f["internId"] in ids], "timestamp")


# ---- daily logs -----------------------------------------------------------------------------

@router.get("/daily-logs")
def daily_logs(user: dict = Depends(admin_only), store=Depends(get_store)):
    ids = {i["id"] for i in _org_interns(store, user)}
    return sorted_desc([l for l in store.list("daily_logs") if l["internId"] in ids], "date")


class ReviewIn(BaseModel):
    status: Literal["Approved", "Rejected"]
    comment: str = ""


@router.post("/daily-logs/{log_id}/review")
def review_log(log_id: str, body: ReviewIn, user: dict = Depends(admin_only), store=Depends(get_store)):
    log = store.get("daily_logs", log_id)
    if not log:
        raise HTTPException(404, "Daily log not found")
    _own_intern(store, user, log["internId"])
    updated = store.update("daily_logs", log_id, {
        "status": body.status, "reviewerComment": body.comment or log["reviewerComment"], "reviewedAt": stamp(),
    })
    audit(store, user["name"], f"{body.status} daily log", log["date"])
    return updated


# ---- evaluations ----------------------------------------------------------------------------

class Criterion(BaseModel):
    label: str
    score: float = Field(ge=0, le=5)


class EvaluationIn(BaseModel):
    internId: str
    period: str
    criteria: list[Criterion] = Field(min_length=1)
    comments: str = ""
    status: Literal["Draft", "Released"] = "Draft"


@router.get("/evaluations")
def evaluations(user: dict = Depends(admin_only), store=Depends(get_store)):
    ids = {i["id"] for i in _org_interns(store, user)}
    return sorted_desc([e for e in store.list("evaluations") if e["internId"] in ids], "createdAt")


def _notify_released(store, intern_id: str, period: str) -> None:
    store.insert("notifications", {
        "id": new_id("n"), "userId": intern_id, "title": "Evaluation released",
        "body": f"Your {period} evaluation is now available to view.", "time": stamp(),
        "read": False, "tone": "primary",
    })


@router.post("/evaluations", status_code=201)
def create_evaluation(body: EvaluationIn, user: dict = Depends(admin_only), store=Depends(get_store)):
    intern = _own_intern(store, user, body.internId)
    rating = round(sum(c.score for c in body.criteria) / len(body.criteria), 1)
    row = store.insert("evaluations", {
        "id": new_id("eval"), "internId": intern["id"], "evaluatorId": user["id"], "evaluatorName": user["name"],
        "period": body.period, "rating": rating, "status": body.status, "comments": body.comments,
        "createdAt": stamp().split(" ")[0], "criteria": [c.model_dump() for c in body.criteria],
    })
    if body.status == "Released":
        _notify_released(store, intern["id"], body.period)
    audit(store, user["name"], "Released evaluation" if body.status == "Released" else "Created evaluation",
          f"{intern['name']} — {body.period}")
    return row


@router.post("/evaluations/{eval_id}/release")
def release_evaluation(eval_id: str, user: dict = Depends(admin_only), store=Depends(get_store)):
    ev = store.get("evaluations", eval_id)
    if not ev:
        raise HTTPException(404, "Evaluation not found")
    _own_intern(store, user, ev["internId"])
    updated = store.update("evaluations", eval_id, {"status": "Released"})
    _notify_released(store, ev["internId"], ev["period"])
    audit(store, user["name"], "Released evaluation", ev["period"])
    return updated


# ---- locations ------------------------------------------------------------------------------

class LocationIn(BaseModel):
    name: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius: float = Field(gt=0, le=5000)
    status: Literal["Active", "Inactive"] = "Active"


@router.get("/locations")
def locations(user: dict = Depends(admin_only), store=Depends(get_store)):
    return store.list("locations", {"orgId": user["orgId"]})


@router.post("/locations", status_code=201)
def add_location(body: LocationIn, user: dict = Depends(admin_only), store=Depends(get_store)):
    row = store.insert("locations", {"id": new_id("loc"), "orgId": user["orgId"], **body.model_dump()})
    audit(store, user["name"], "Added attendance location", f"{body.name} ({round(body.radius)}m)")
    return row


@router.put("/locations/{loc_id}")
def update_location(loc_id: str, body: LocationIn, user: dict = Depends(admin_only), store=Depends(get_store)):
    loc = store.get("locations", loc_id)
    if not loc or loc["orgId"] != user["orgId"]:
        raise HTTPException(404, "Location not found")
    row = store.update("locations", loc_id, body.model_dump())
    audit(store, user["name"], "Updated attendance location", f"{body.name} ({round(body.radius)}m)")
    return row


@router.delete("/locations/{loc_id}", status_code=204)
def delete_location(loc_id: str, user: dict = Depends(admin_only), store=Depends(get_store)):
    loc = store.get("locations", loc_id)
    if not loc or loc["orgId"] != user["orgId"]:
        raise HTTPException(404, "Location not found")
    store.delete("locations", loc_id)
    audit(store, user["name"], "Removed attendance location", loc["name"])


# ---- audit ----------------------------------------------------------------------------------

@router.get("/audit-logs")
def audit_logs(user: dict = Depends(admin_only), store=Depends(get_store)):
    """Recent activity by this organization's admins and trainees (audit rows are keyed by display name)."""
    names = {i["name"] for i in _org_interns(store, user)} | {a["name"] for a in store.list("admins", {"orgId": user["orgId"]})}
    return sorted_desc([l for l in store.list("audit_logs") if l["user"] in names], "timestamp")[:50]


# ---- reports --------------------------------------------------------------------------------

@router.get("/reports/summary")
def report_summary(user: dict = Depends(admin_only), store=Depends(get_store)):
    interns = _org_interns(store, user)
    by_status: dict[str, int] = {}
    for i in interns:
        by_status[i["internshipStatus"]] = by_status.get(i["internshipStatus"], 0) + 1
    total = sum(i["renderedHours"] or 0 for i in interns)
    return {
        "totalInterns": len(interns),
        "statusBreakdown": by_status,
        "totalHours": round(total, 1),
        "averageHours": round(total / len(interns), 1) if interns else 0,
        "progress": [
            {"id": i["id"], "name": i["name"], "renderedHours": i["renderedHours"],
             "requiredHours": i["requiredHours"], "internshipStatus": i["internshipStatus"]}
            for i in interns
        ],
    }
