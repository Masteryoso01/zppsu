from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..deps import audit, get_store, new_id, now, require_role, sorted_desc, stamp
from ..security import hash_password
from ..stats import attendance_stats

router = APIRouter(prefix="/api/super-admin", tags=["super-admin"])
super_only = require_role("super-admin")


@router.get("/overview")
def overview(user: dict = Depends(super_only), store=Depends(get_store)):
    orgs, interns, admins = store.list("organizations"), store.list("interns"), store.list("admins")
    today = stamp().split(" ")[0]
    return {
        "organizations": len(orgs),
        "activeOrganizations": sum(1 for o in orgs if o["status"] == "Active"),
        "totalInterns": sum(1 for i in interns if i["applicationStatus"] == "Approved"),
        "pendingApplications": sum(1 for i in interns if i["applicationStatus"] == "Pending"),
        "adminAccounts": len(admins),
        "todayAttendance": sum(1 for a in store.list("attendance") if a["date"] == today),
    }


# ---- applications & deployment --------------------------------------------------------------

@router.get("/applications")
def applications(
    status: Literal["Pending", "Approved", "Rejected"] | None = Query(None),
    user: dict = Depends(super_only), store=Depends(get_store),
):
    rows = store.list("interns", {"applicationStatus": status} if status else None)
    return rows


class DeployIn(BaseModel):
    orgId: str


def _active_org(store, org_id: str) -> dict:
    org = store.get("organizations", org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    if org["status"] != "Active":
        raise HTTPException(409, "Cannot deploy to an inactive organization")
    return org


def _intern(store, intern_id: str) -> dict:
    row = store.get("interns", intern_id)
    if not row:
        raise HTTPException(404, "OJT trainee not found")
    return row


def _deploy_patch(store, org_id: str) -> dict:
    programs = store.list("programs", {"orgId": org_id})
    program = next((p for p in programs if p["status"] == "Active"), None)
    patch = {"orgId": org_id, "programId": program["id"] if program else None}
    if program:
        patch["requiredHours"] = program["requiredHours"]
    return patch


@router.post("/applications/{intern_id}/approve")
def approve(intern_id: str, body: DeployIn, user: dict = Depends(super_only), store=Depends(get_store)):
    intern = _intern(store, intern_id)
    if intern["applicationStatus"] == "Rejected":
        raise HTTPException(409, "This application was rejected")
    org = _active_org(store, body.orgId)
    patch = {"applicationStatus": "Approved", "internshipStatus": "Ongoing", **_deploy_patch(store, org["id"])}
    if not intern["startDate"]:
        patch["startDate"] = stamp().split(" ")[0]
    row = store.update("interns", intern_id, patch)
    store.update("users", intern_id, {"orgId": org["id"]})
    store.insert("notifications", {
        "id": new_id("n"), "userId": intern_id, "title": "Application approved",
        "body": f"You have been deployed to {org['name']}.", "time": stamp(), "read": False, "tone": "success",
    })
    audit(store, user["name"], "Approved and deployed OJT trainee", f"{intern['name']} → {org['name']}")
    return row


@router.post("/applications/{intern_id}/deploy")
def redeploy(intern_id: str, body: DeployIn, user: dict = Depends(super_only), store=Depends(get_store)):
    intern = _intern(store, intern_id)
    if intern["applicationStatus"] != "Approved":
        raise HTTPException(409, "Only approved trainees can be deployed")
    org = _active_org(store, body.orgId)
    row = store.update("interns", intern_id, _deploy_patch(store, org["id"]))
    store.update("users", intern_id, {"orgId": org["id"]})
    audit(store, user["name"], "Deployed OJT trainee", f"{intern['name']} → {org['name']}")
    return row


@router.post("/applications/{intern_id}/reject")
def reject(intern_id: str, user: dict = Depends(super_only), store=Depends(get_store)):
    intern = _intern(store, intern_id)
    row = store.update("interns", intern_id, {"applicationStatus": "Rejected", "internshipStatus": "Not Started"})
    audit(store, user["name"], "Rejected application", intern["name"])
    return row


# ---- organizations --------------------------------------------------------------------------

class OrgIn(BaseModel):
    name: str = Field(min_length=2)
    address: str = ""
    status: Literal["Active", "Suspended"] = "Active"


def _org_view(store, org: dict) -> dict:
    return {
        **org,
        "admins": len(store.list("admins", {"orgId": org["id"]})),
        "interns": len([i for i in store.list("interns", {"orgId": org["id"]})]),
    }


@router.get("/organizations")
def organizations(user: dict = Depends(super_only), store=Depends(get_store)):
    return [_org_view(store, o) for o in store.list("organizations")]


@router.get("/organizations/{org_id}/trainees")
def organization_trainees(org_id: str, user: dict = Depends(super_only), store=Depends(get_store)):
    """Approved trainees deployed to this organization, with attendance/absence stats (most absences first)."""
    store.prefetch(["organizations", "interns", "attendance", "admins"])
    org = store.get("organizations", org_id)
    if not org:
        raise HTTPException(404, "Organization not found")
    interns = [i for i in store.list("interns", {"orgId": org_id}) if i["applicationStatus"] == "Approved"]
    ids = {i["id"] for i in interns}
    records = [a for a in store.list("attendance") if a["internId"] in ids]
    today = now().date()
    trainees = [{**i, "stats": attendance_stats(i, records, today)} for i in interns]
    trainees.sort(key=lambda t: (-t["stats"]["daysAbsent"], t["name"]))
    rates = [t["stats"]["attendanceRate"] for t in trainees if t["stats"]["attendanceRate"] is not None]
    return {
        "organization": _org_view(store, org),
        "trainees": trainees,
        "summary": {
            "totalTrainees": len(trainees),
            "frequentAbsentees": sum(1 for t in trainees if t["stats"]["frequentAbsent"]),
            "totalAbsences": sum(t["stats"]["daysAbsent"] for t in trainees),
            "averageAttendanceRate": round(sum(rates) / len(rates)) if rates else None,
        },
    }


@router.post("/organizations", status_code=201)
def add_org(body: OrgIn, user: dict = Depends(super_only), store=Depends(get_store)):
    org = store.insert("organizations", {"id": new_id("org"), **body.model_dump(), "createdAt": stamp().split(" ")[0]})
    audit(store, user["name"], "Created organization", body.name)
    return _org_view(store, org)


@router.put("/organizations/{org_id}")
def update_org(org_id: str, body: OrgIn, user: dict = Depends(super_only), store=Depends(get_store)):
    if not store.get("organizations", org_id):
        raise HTTPException(404, "Organization not found")
    org = store.update("organizations", org_id, body.model_dump())
    audit(store, user["name"], f"Updated organization ({body.status})", body.name)
    return _org_view(store, org)


# ---- admin accounts -------------------------------------------------------------------------

class AdminIn(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    orgId: str
    password: str = Field(min_length=8)


class AdminStatusIn(BaseModel):
    status: Literal["Active", "Inactive"]


@router.get("/admins")
def admins(user: dict = Depends(super_only), store=Depends(get_store)):
    return store.list("admins")


@router.post("/admins", status_code=201)
def add_admin(body: AdminIn, user: dict = Depends(super_only), store=Depends(get_store)):
    email = body.email.strip().lower()
    if store.list("users", {"email": email}):
        raise HTTPException(409, "An account with this email already exists")
    org = store.get("organizations", body.orgId)
    if not org:
        raise HTTPException(404, "Organization not found")
    admin_id = new_id("adm")
    row = store.insert("admins", {
        "id": admin_id, "name": body.name.strip(), "email": email, "orgId": body.orgId, "status": "Active",
        "lastLogin": None,
    })
    store.insert("users", {
        "id": admin_id, "email": email, "passwordHash": hash_password(body.password), "role": "admin",
        "name": body.name.strip(), "orgId": body.orgId, "status": "Active", "createdAt": stamp(),
    })
    audit(store, user["name"], "Created admin account", f"{body.name} ({org['name']})")
    return row


@router.patch("/admins/{admin_id}")
def set_admin_status(admin_id: str, body: AdminStatusIn, user: dict = Depends(super_only), store=Depends(get_store)):
    row = store.update("admins", admin_id, {"status": body.status})
    if not row:
        raise HTTPException(404, "Admin not found")
    store.update("users", admin_id, {"status": body.status})
    audit(store, user["name"], f"Set admin {body.status.lower()}", row["name"])
    return row


# ---- audit logs & reports -------------------------------------------------------------------

@router.get("/audit-logs")
def audit_logs(limit: int = Query(200, ge=1, le=1000), user: dict = Depends(super_only), store=Depends(get_store)):
    return sorted_desc(store.list("audit_logs"), "timestamp")[:limit]


@router.get("/reports/summary")
def report_summary(user: dict = Depends(super_only), store=Depends(get_store)):
    interns = [i for i in store.list("interns") if i["applicationStatus"] == "Approved"]
    orgs = store.list("organizations")
    total = sum(i["renderedHours"] or 0 for i in interns)
    return {
        "totalInterns": len(interns),
        "totalHours": round(total, 1),
        "averageHours": round(total / len(interns), 1) if interns else 0,
        "internsByOrganization": [
            {"orgId": o["id"], "name": o["name"], "interns": sum(1 for i in interns if i["orgId"] == o["id"])}
            for o in orgs
        ],
    }
