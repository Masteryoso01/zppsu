"""Seed the data store.

    python -m app.seed          # creates only the first Super Admin
    python -m app.seed --demo   # also loads demo organizations / admins / trainees

Safe to re-run: existing rows (matched by id/email) are skipped.
"""
import sys
from datetime import timedelta

from .config import get_settings
from .deps import get_store, now, stamp
from .security import hash_password

DEMO_PASSWORD = "Demo12345!"


def _insert_missing(store, table: str, rows: list[dict], key: str = "id") -> int:
    existing = {r[key] for r in store.list(table)}
    fresh = [r for r in rows if r[key] not in existing]
    store.insert_many(table, fresh)
    return len(fresh)


def seed(demo: bool = False) -> None:
    s, store = get_settings(), get_store()
    today = stamp().split(" ")[0]

    sa_email = s.superadmin_email.strip().lower()
    n = _insert_missing(store, "users", [{
        "id": "sa-1", "email": sa_email, "passwordHash": hash_password(s.superadmin_password),
        "role": "super-admin", "name": "System Administrator", "orgId": None, "status": "Active", "createdAt": stamp(),
    }])
    print(f"super admin: {sa_email} ({'created' if n else 'already exists'})")

    if not demo:
        return

    _insert_missing(store, "organizations", [
        {"id": "org-1", "name": "Northbridge Institute of Technology", "address": "Quezon City, Metro Manila", "status": "Active", "createdAt": "2024-01-12"},
        {"id": "org-2", "name": "Riverside College of Business", "address": "Cebu City, Cebu", "status": "Active", "createdAt": "2024-03-04"},
    ])
    _insert_missing(store, "programs", [
        {"id": "prog-1", "orgId": "org-1", "name": "IT Practicum — On-the-Job Training", "description": "BSIT/BSCS capstone OJT placement", "requiredHours": 486, "status": "Active"},
        {"id": "prog-2", "orgId": "org-2", "name": "Accounting OJT", "description": "BSA OJT track", "requiredHours": 500, "status": "Active"},
    ])
    _insert_missing(store, "locations", [
        {"id": "loc-1", "orgId": "org-1", "name": "Main Office — 4th Floor", "latitude": 14.6507, "longitude": 121.0494, "radius": 100, "status": "Active"},
        {"id": "loc-2", "orgId": "org-2", "name": "Riverside Main Campus", "latitude": 10.3157, "longitude": 123.8854, "radius": 120, "status": "Active"},
    ])
    admins = [
        {"id": "adm-1", "name": "Marielle Custodio", "email": "marielle.custodio@northbridge.edu", "orgId": "org-1", "status": "Active", "lastLogin": None},
        {"id": "adm-2", "name": "Joan Villareal", "email": "joan.villareal@riverside.edu", "orgId": "org-2", "status": "Active", "lastLogin": None},
    ]
    _insert_missing(store, "admins", admins)
    _insert_missing(store, "users", [
        {"id": a["id"], "email": a["email"], "passwordHash": hash_password(DEMO_PASSWORD), "role": "admin",
         "name": a["name"], "orgId": a["orgId"], "status": "Active", "createdAt": stamp()}
        for a in admins
    ])

    def intern(i, name, email, student_id, status, org, prog, hours=0.0, internship="Not Started"):
        return {
            "id": i, "orgId": org, "programId": prog, "name": name, "email": email, "studentId": student_id,
            "school": "Northbridge Institute of Technology", "course": "BS Information Technology",
            "yearLevel": "4th Year", "contact": "0917 234 5678", "address": "Quezon City", "avatarColor": "primary",
            "applicationStatus": status, "requiredHours": 486, "renderedHours": hours, "faceStatus": "Enrolled",
            "internshipStatus": internship, "startDate": today if status == "Approved" else None, "endDate": None,
        }

    interns = [
        intern("intern-1", "Jhon Michael Dela Cruz", "jhon.delacruz@student.northbridge.edu", "2021-00214-NT", "Approved", "org-1", "prog-1", 12.5, "Ongoing"),
        intern("intern-2", "Angelica Ramos", "angelica.ramos@student.northbridge.edu", "2021-00337-NT", "Approved", "org-1", "prog-1", 0, "Ongoing"),
        intern("intern-3", "Marc Anthony Buenaventura", "marc.buenaventura@student.northbridge.edu", "2021-00118-NT", "Pending", None, None),
    ]
    _insert_missing(store, "interns", interns)
    _insert_missing(store, "users", [
        {"id": i["id"], "email": i["email"], "passwordHash": hash_password(DEMO_PASSWORD), "role": "intern",
         "name": i["name"], "orgId": i["orgId"], "status": "Active", "createdAt": stamp()}
        for i in interns
    ])
    _seed_attendance_history(store)
    print(f"demo data loaded. Demo logins use password: {DEMO_PASSWORD}")
    print("  admin : marielle.custodio@northbridge.edu")
    print("  intern: jhon.delacruz@student.northbridge.edu (deployed), marc.buenaventura@student.northbridge.edu (pending)")


def _seed_attendance_history(store) -> None:
    """Give the two deployed demo trainees three weeks of history so absence stats have something to show.

    intern-1 attends nearly every working day; intern-2 is deliberately a frequent absentee.
    """
    today = now().date()
    start = today - timedelta(days=21)
    for iid in ("intern-1", "intern-2"):
        intern = store.get("interns", iid)
        if intern and (not intern["startDate"] or intern["startDate"] > start.isoformat()):
            store.update("interns", iid, {"startDate": start.isoformat()})

    days = [start + timedelta(days=n) for n in range(21) if (start + timedelta(days=n)).weekday() < 5 and start + timedelta(days=n) < today]
    rows = []
    for n, d in enumerate(days):
        attending = []
        if n != 4:  # intern-1 misses a single day
            attending.append(("intern-1", "08:41" if n % 6 == 0 else "07:58"))
        if n % 3 == 0:  # intern-2 shows up roughly one day in three
            attending.append(("intern-2", "08:02"))
        for iid, tin in attending:
            late = tin > "08:15"
            rows.append({"id": f"att-demo-{iid}-{d}-in", "internId": iid, "locationId": "loc-1", "type": "Time In", "date": d.isoformat(),
                         "timestamp": f"{d} {tin}", "status": "Late" if late else "On Time", "distance": 15,
                         "faceVerified": True, "livenessVerified": True, "gpsVerified": True, "method": "Fingerprint"})
            rows.append({"id": f"att-demo-{iid}-{d}-out", "internId": iid, "locationId": "loc-1", "type": "Time Out", "date": d.isoformat(),
                         "timestamp": f"{d} 17:02", "status": "Completed", "distance": 12,
                         "faceVerified": True, "livenessVerified": True, "gpsVerified": True, "method": "Fingerprint"})
    n = _insert_missing(store, "attendance", rows)
    print(f"demo attendance history: {n} new records")


if __name__ == "__main__":
    seed(demo="--demo" in sys.argv)
