# GeoTrack — API Plan

## Authentication
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/forgot-password
POST /api/auth/reset-password

## OJT Trainee
GET /api/intern/profile
PUT /api/intern/profile
GET /api/intern/application
GET /api/intern/requirements
POST /api/intern/documents
GET /api/intern/attendance
GET /api/intern/progress
GET /api/intern/daily-logs
POST /api/intern/daily-logs

## Face
POST /api/intern/face/enroll
GET /api/intern/face/status
POST /api/attendance/face/verify

## Attendance
POST /api/attendance/time-in
POST /api/attendance/time-out
GET /api/attendance/today
GET /api/attendance/history

## Admin
GET /api/admin/applications
POST /api/admin/applications/{id}/approve
POST /api/admin/applications/{id}/reject

GET /api/admin/interns
GET /api/admin/interns/{id}

GET /api/admin/attendance
GET /api/admin/daily-logs
POST /api/admin/daily-logs/{id}/approve
POST /api/admin/daily-logs/{id}/reject

GET /api/admin/reports/attendance
GET /api/admin/reports/progress

## Organization
GET /api/admin/locations
POST /api/admin/locations
PUT /api/admin/locations/{id}

GET /api/admin/requirements
POST /api/admin/requirements
PUT /api/admin/requirements/{id}

## Super Admin
GET /api/super-admin/organizations
POST /api/super-admin/organizations
PUT /api/super-admin/organizations/{id}

GET /api/super-admin/admins
POST /api/super-admin/admins
PUT /api/super-admin/admins/{id}

GET /api/super-admin/audit-logs

## API Rules
- Validate all input server-side.
- Enforce authorization on every protected endpoint.
- Never trust role values sent by the frontend.
- Never let the frontend directly mark attendance as valid.
- Attendance validity is decided by backend business logic.
- Sensitive biometric/file endpoints require strict authorization.
