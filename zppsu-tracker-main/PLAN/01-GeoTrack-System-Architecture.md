# GeoTrack — System Architecture

## Whole-System Diagram

```text
                         GEOTRACK
                            |
          +-----------------+-----------------+
          |                 |                 |
     SUPER ADMIN          ADMIN             INTERN
          |                 |                 |
          +-----------------+-----------------+
                            |
                            v
                    +---------------+
                    |   FRONTEND    |
                    | React/Vite    |
                    | Tailwind      |
                    +-------+-------+
                            |
                           HTTPS
                            |
                            v
                    +---------------+
                    |   REST API    |
                    | PHP/Laravel   |
                    +-------+-------+
                            |
        +-------------------+-------------------+
        |                   |                   |
        v                   v                   v
   AUTH/RBAC          BUSINESS LOGIC       FILE STORAGE
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
 OJT                  Attendance          Documents
 Management             Management
                            |
                    +-------+-------+
                    |       |       |
                    v       v       v
                  Face   Liveness   GPS
                 Verify  Check      Check
                    |       |       |
                    +-------+-------+
                            |
                            v
                         MySQL
                            |
                            v
                       Audit Logs
```

## Layer Responsibilities

### Frontend
Responsible for:
- UI
- Camera permission
- GPS permission
- Form validation
- API calls
- Dashboard rendering
- Attendance workflow UI

Frontend must not be the final authority for attendance validity.

### API
Responsible for:
- Authentication
- Authorization
- Input validation
- Business rules
- Verification orchestration
- Database writes
- Audit logging

### Services
Recommended services:
- AuthService
- InternService
- InternshipService
- DocumentService
- FaceVerificationService
- LivenessService
- GeolocationService
- AttendanceService
- DailyLogService
- ReportService
- AuditService

### Database
Stores application data, not arbitrary sensitive files.

### File Storage
Stores approved document files and other required uploads with access controls.

## Attendance Architecture

```text
TIME IN / TIME OUT
        |
        v
 Camera Capture
        |
        v
 Face Detection
        |
        v
 Face Verification
        |
        v
 Liveness Detection
        |
        v
 GPS Validation
        |
        v
 Schedule Validation
        |
        v
 AttendanceService
        |
        +--> attendance record
        +--> verification evidence
        +--> audit log
```

## Design Rule
Controllers should orchestrate requests, not contain all business logic. Put reusable business rules in services.

## Security Boundaries
- HTTPS between client and API
- RBAC and organization-level authorization
- Password hashing
- Secure document storage
- Restricted biometric access
- Rate limiting
- Input/file validation
- Audit logs
- Secure environment secrets
