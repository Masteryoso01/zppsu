# GeoTrack — Development Roadmap

## Step 1 — Foundation
- Create repositories
- Configure frontend/backend
- Configure environment variables
- Set up MySQL
- Set up migrations
- Implement authentication
- Implement RBAC

## Step 2 — Organizations and Users
- Super Admin organization management
- Admin management
- OJT Trainee profiles
- Organization isolation

## Step 3 — OJT Onboarding
- OJT Trainee registration
- Student information
- OJT programs
- Required documents
- Document upload/review
- Admin approval

## Step 4 — Face Enrollment
- Camera flow
- Face detection
- Face quality checks
- Face template generation
- Secure storage
- Enrollment status

## Step 5 — Attendance
- Time In
- Time Out
- Face verification
- Liveness
- GPS
- Radius validation
- Schedule rules
- Attendance records
- Audit logs

## Step 6 — Monitoring
- Daily logs
- Rendered hours
- Progress calculation
- Admin review
- Evaluation

## Step 7 — Reports
- Attendance reports
- Progress reports
- Completion reports
- Export

## Step 8 — Hardening
- Security testing
- Authorization testing
- File upload testing
- Face verification testing
- Liveness testing
- GPS edge cases
- Rate limiting
- Backup/restore

## Step 9 — Deployment
Development -> Staging/UAT -> Production

## Definition of Done
A feature is not complete until:
- UI works
- API works
- Server-side authorization works
- Validation works
- Database changes are migrated
- Error handling exists
- Audit/security implications are addressed
- Tests cover important business rules
- Documentation is updated
