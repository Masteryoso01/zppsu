"""Table layout. Must match SCHEMA in apps-script/Code.gs (same tables, same column order)."""

TABLES: dict[str, list[str]] = {
    "organizations": ["id", "name", "address", "status", "createdAt"],
    "users": ["id", "email", "passwordHash", "role", "name", "orgId", "status", "createdAt"],
    "admins": ["id", "name", "email", "orgId", "status", "lastLogin"],
    "programs": ["id", "orgId", "name", "description", "requiredHours", "status"],
    "locations": ["id", "orgId", "name", "latitude", "longitude", "radius", "status"],
    "interns": [
        "id", "orgId", "programId", "name", "email", "studentId", "school", "course", "yearLevel", "contact",
        "address", "avatarColor", "applicationStatus", "requiredHours", "renderedHours", "faceStatus",
        "internshipStatus", "startDate", "endDate",
    ],
    "attendance": [
        "id", "internId", "locationId", "type", "date", "timestamp", "status", "distance",
        "faceVerified", "livenessVerified", "gpsVerified", "method",
    ],
    "failed_attempts": ["id", "internId", "date", "timestamp", "reason", "stage"],
    "daily_logs": [
        "id", "internId", "date", "activities", "learnings", "challenges", "status", "reviewerComment", "reviewedAt",
    ],
    "evaluations": [
        "id", "internId", "evaluatorId", "evaluatorName", "period", "rating", "status", "comments", "createdAt",
        "criteria",
    ],
    "audit_logs": ["id", "user", "action", "resource", "result", "timestamp"],
    "notifications": ["id", "userId", "title", "body", "time", "read", "tone"],
}
