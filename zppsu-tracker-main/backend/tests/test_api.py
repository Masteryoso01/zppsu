import os

os.environ["STORE"] = "memory"
os.environ["SUPERADMIN_EMAIL"] = "root@test.io"
os.environ["SUPERADMIN_PASSWORD"] = "RootPass123!"
os.environ["JWT_SECRET"] = "test-secret-test-secret-test-secret"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import seed  # noqa: E402
from app.deps import get_store  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    get_store.cache_clear()
    seed.seed(demo=True)
    return TestClient(app)


def login(client, email, password):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_login_and_role_guards(client):
    assert client.post("/api/auth/login", json={"email": "root@test.io", "password": "nope"}).status_code == 401
    sa = login(client, "root@test.io", "RootPass123!")
    assert client.get("/api/super-admin/overview", headers=sa).status_code == 200
    assert client.get("/api/admin/interns", headers=sa).status_code == 403
    assert client.get("/api/super-admin/overview").status_code == 401


def test_register_approve_deploy_flow(client):
    r = client.post("/api/auth/register", json={
        "fullName": "Test Trainee", "studentId": "2022-00001", "email": "Test@Student.edu", "contact": "09171234567",
        "school": "ZPPSU", "course": "BSIT", "yearLevel": "4th Year", "password": "Password123", "biometricRegistered": True,
    })
    assert r.status_code == 201
    intern_id = r.json()["id"]
    dup = client.post("/api/auth/register", json={
        "fullName": "Dup", "studentId": "2022-00002", "email": "test@student.edu", "contact": "09171234567",
        "school": "x", "course": "y", "yearLevel": "1st Year", "password": "Password123",
    })
    assert dup.status_code == 409

    trainee = login(client, "test@student.edu", "Password123")
    # Not deployed yet -> cannot submit logs
    assert client.post("/api/intern/daily-logs", headers=trainee, json={"date": "2026-11-02", "activities": "x"}).status_code == 403

    sa = login(client, "root@test.io", "RootPass123!")
    pending = client.get("/api/super-admin/applications?status=Pending", headers=sa).json()
    assert intern_id in {p["id"] for p in pending}
    assert client.post(f"/api/super-admin/applications/{intern_id}/approve", headers=sa, json={"orgId": "nope"}).status_code == 404
    ok = client.post(f"/api/super-admin/applications/{intern_id}/approve", headers=sa, json={"orgId": "org-2"})
    assert ok.status_code == 200 and ok.json()["orgId"] == "org-2" and ok.json()["requiredHours"] == 500

    trainee = login(client, "test@student.edu", "Password123")
    prof = client.get("/api/intern/profile", headers=trainee).json()
    assert prof["organization"]["id"] == "org-2" and len(prof["locations"]) == 1
    assert client.post("/api/intern/daily-logs", headers=trainee, json={"date": "2026-11-02", "activities": "did stuff"}).status_code == 201

    moved = client.post(f"/api/super-admin/applications/{intern_id}/deploy", headers=sa, json={"orgId": "org-1"})
    assert moved.json()["orgId"] == "org-1"


def test_attendance_geofence_and_hours(client):
    t = login(client, "jhon.delacruz@student.northbridge.edu", "Demo12345!")
    far = client.post("/api/intern/attendance", headers=t, json={"locationId": "loc-1", "latitude": 14.70, "longitude": 121.10})
    assert far.status_code == 422 and "Outside allowed radius" in far.json()["detail"]
    assert len(client.get("/api/intern/failed-attempts", headers=t).json()) == 1

    near = {"locationId": "loc-1", "latitude": 14.6507, "longitude": 121.0494, "method": "Fingerprint"}
    tin = client.post("/api/intern/attendance", headers=t, json=near)
    assert tin.status_code == 201 and tin.json()["type"] == "Time In"
    tout = client.post("/api/intern/attendance", headers=t, json=near)
    assert tout.status_code == 201 and tout.json()["type"] == "Time Out"
    assert client.post("/api/intern/attendance", headers=t, json=near).status_code == 409
    # Another org's location is not usable
    assert client.post("/api/intern/attendance", headers=t, json={**near, "locationId": "loc-2"}).status_code in (404, 409)


def test_admin_scoped_to_org_and_reviews_logs(client):
    t = login(client, "jhon.delacruz@student.northbridge.edu", "Demo12345!")
    log = client.post("/api/intern/daily-logs", headers=t, json={"date": "2026-11-02", "activities": "Built a page"}).json()

    a1 = login(client, "marielle.custodio@northbridge.edu", "Demo12345!")
    a2 = login(client, "joan.villareal@riverside.edu", "Demo12345!")
    assert {i["id"] for i in client.get("/api/admin/interns", headers=a1).json()} == {"intern-1", "intern-2"}
    assert client.get("/api/admin/interns", headers=a2).json() == []
    assert client.get("/api/admin/interns/intern-1", headers=a2).status_code == 404
    assert client.post(f"/api/admin/daily-logs/{log['id']}/review", headers=a2, json={"status": "Approved"}).status_code == 404

    rv = client.post(f"/api/admin/daily-logs/{log['id']}/review", headers=a1, json={"status": "Approved", "comment": "Nice"})
    assert rv.status_code == 200 and rv.json()["status"] == "Approved"


def test_evaluation_release_and_locations(client):
    a1 = login(client, "marielle.custodio@northbridge.edu", "Demo12345!")
    ev = client.post("/api/admin/evaluations", headers=a1, json={
        "internId": "intern-1", "period": "Midterm", "criteria": [{"label": "Skills", "score": 4}, {"label": "Attitude", "score": 5}],
    })
    assert ev.status_code == 201 and ev.json()["rating"] == 4.5 and ev.json()["status"] == "Draft"
    t = login(client, "jhon.delacruz@student.northbridge.edu", "Demo12345!")
    assert client.get("/api/intern/evaluations", headers=t).json() == []
    assert client.post(f"/api/admin/evaluations/{ev.json()['id']}/release", headers=a1).status_code == 200
    assert len(client.get("/api/intern/evaluations", headers=t).json()) == 1
    assert len(client.get("/api/intern/notifications", headers=t).json()) == 1

    loc = client.post("/api/admin/locations", headers=a1, json={"name": "Annex", "latitude": 14.65, "longitude": 121.05, "radius": 75})
    assert loc.status_code == 201
    assert client.delete(f"/api/admin/locations/{loc.json()['id']}", headers=a1).status_code == 204


def test_super_admin_manages_orgs_and_admins(client):
    sa = login(client, "root@test.io", "RootPass123!")
    org = client.post("/api/super-admin/organizations", headers=sa, json={"name": "New College", "address": "Davao"}).json()
    adm = client.post("/api/super-admin/admins", headers=sa, json={
        "name": "New Admin", "email": "new@admin.edu", "orgId": org["id"], "password": "AdminPass123",
    })
    assert adm.status_code == 201
    assert login(client, "new@admin.edu", "AdminPass123")
    client.patch(f"/api/super-admin/admins/{adm.json()['id']}", headers=sa, json={"status": "Inactive"})
    assert client.post("/api/auth/login", json={"email": "new@admin.edu", "password": "AdminPass123"}).status_code == 403
    assert client.get("/api/super-admin/audit-logs", headers=sa).json()


def test_organization_trainees_absence_stats(client):
    from datetime import timedelta

    from app.deps import now

    store = get_store()
    today = now().date()
    store._data["attendance"].clear()  # drop the seeded demo history; this test builds its own
    # Start 3 weeks ago; intern-1 attends every working day, intern-2 attends only two days.
    start = today - timedelta(days=21)
    for iid in ("intern-1", "intern-2"):
        store.update("interns", iid, {"startDate": start.isoformat()})
    days = [start + timedelta(days=n) for n in range(21) if (start + timedelta(days=n)).weekday() < 5]
    for n, d in enumerate(days):
        who = ["intern-1"] + (["intern-2"] if n < 2 else [])
        for iid in who:
            store.insert("attendance", {
                "id": f"att-t-{iid}-{d}", "internId": iid, "locationId": "loc-1", "type": "Time In", "date": d.isoformat(),
                "timestamp": f"{d} 08:00", "status": "Late" if n == 0 and iid == "intern-1" else "On Time", "distance": 10,
            })

    sa = login(client, "root@test.io", "RootPass123!")
    res = client.get("/api/super-admin/organizations/org-1/trainees", headers=sa)
    assert res.status_code == 200
    body = res.json()
    assert body["organization"]["interns"] == 2 and body["summary"]["totalTrainees"] == 2
    t = {x["id"]: x["stats"] for x in body["trainees"]}
    working = len(days)  # today is excluded; compute the same way the API does
    expected_days = len([d for d in days if d < today])
    assert t["intern-1"]["daysAbsent"] == 0 and t["intern-1"]["lateCount"] == 1 and not t["intern-1"]["frequentAbsent"]
    assert t["intern-2"]["workingDays"] == expected_days
    assert t["intern-2"]["daysAbsent"] == expected_days - 2 and t["intern-2"]["frequentAbsent"] is True
    assert len(t["intern-2"]["recentAbsences"]) == 5
    assert body["trainees"][0]["id"] == "intern-2"  # most absences first
    assert body["summary"]["frequentAbsentees"] == 1

    # Pending applicants are not "assigned" trainees; unknown org and non-super-admin are rejected.
    assert client.get("/api/super-admin/organizations/nope/trainees", headers=sa).status_code == 404
    admin = login(client, "marielle.custodio@northbridge.edu", "Demo12345!")
    assert client.get("/api/super-admin/organizations/org-1/trainees", headers=admin).status_code == 403
