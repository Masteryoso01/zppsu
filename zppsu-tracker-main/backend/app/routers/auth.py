from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..deps import audit, current_user, get_store, new_id, org_name, stamp
from ..security import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginIn(BaseModel):
    email: str
    password: str


class RegisterIn(BaseModel):
    fullName: str = Field(min_length=2)
    studentId: str = Field(min_length=1)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    contact: str = Field(min_length=7)
    school: str
    course: str
    yearLevel: str
    password: str = Field(min_length=8)
    biometricRegistered: bool = False


def _session(store, user: dict) -> dict:
    return {
        "token": create_token(user),
        "user": {
            "id": user["id"], "role": user["role"], "name": user["name"], "email": user["email"],
            "orgId": user.get("orgId"), "orgName": org_name(store, user.get("orgId")),
        },
    }


@router.post("/login")
def login(body: LoginIn, store=Depends(get_store)):
    users = store.list("users", {"email": body.email.strip().lower()})
    user = users[0] if users else None
    if not user or not verify_password(body.password, user["passwordHash"]):
        raise HTTPException(401, "Incorrect email or password")
    if user["status"] != "Active":
        raise HTTPException(403, "This account is not active")
    # Interns deploy to an org after approval; always read the latest orgId from the intern record.
    if user["role"] == "intern":
        intern = store.get("interns", user["id"])
        user["orgId"] = intern["orgId"] if intern else None
    return _session(store, user)


@router.post("/register", status_code=201)
def register(body: RegisterIn, store=Depends(get_store)):
    email = body.email.strip().lower()
    if store.list("users", {"email": email}):
        raise HTTPException(409, "An account with this email already exists")
    if store.list("interns", {"studentId": body.studentId.strip()}):
        raise HTTPException(409, "This student ID is already registered")

    intern_id = new_id("intern")
    store.insert("interns", {
        "id": intern_id, "orgId": None, "programId": None, "name": body.fullName.strip(), "email": email,
        "studentId": body.studentId.strip(), "school": body.school.strip(), "course": body.course.strip(),
        "yearLevel": body.yearLevel, "contact": body.contact.strip(), "address": "", "avatarColor": "primary",
        "applicationStatus": "Pending", "requiredHours": 486, "renderedHours": 0,
        "faceStatus": "Enrolled" if body.biometricRegistered else "Not Enrolled",
        "internshipStatus": "Not Started", "startDate": None, "endDate": None,
    })
    store.insert("users", {
        "id": intern_id, "email": email, "passwordHash": hash_password(body.password), "role": "intern",
        "name": body.fullName.strip(), "orgId": None, "status": "Active", "createdAt": stamp(),
    })
    audit(store, body.fullName.strip(), "Submitted OJT application", body.studentId.strip())
    return {"id": intern_id, "applicationStatus": "Pending"}


@router.get("/me")
def me(user: dict = Depends(current_user), store=Depends(get_store)):
    row = store.get("users", user["id"])
    if not row or row["status"] != "Active":
        raise HTTPException(401, "Account no longer active")
    if row["role"] == "intern":
        intern = store.get("interns", row["id"])
        row["orgId"] = intern["orgId"] if intern else None
    return {
        "id": row["id"], "role": row["role"], "name": row["name"], "email": row["email"],
        "orgId": row["orgId"], "orgName": org_name(store, row["orgId"]),
    }
