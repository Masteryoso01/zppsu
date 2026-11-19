# GeoTrack — Functional Requirements

## FR-01 Authentication
- Users can log in and log out.
- The system supports Super Admin, Admin, and OJT Trainee roles.
- Unauthorized users cannot access protected resources.
- Role permissions are enforced server-side.

## FR-02 OJT Trainee Registration
OJT Trainee registration must collect:
- Full name
- Student ID number
- Email
- Contact number
- School
- Course/program
- Year level
- Other required profile information

Registration also requires required OJT documents and face enrollment.

## FR-03 Document Management
- Admin can configure required documents.
- OJT Trainee can upload documents.
- Documents have statuses: Pending, Approved, Rejected.
- Rejected documents include a reason.
- OJT Trainee can resubmit rejected documents.
- File type and size must be validated.

## FR-04 Face Enrollment
- OJT Trainee can enroll a face through the camera.
- System detects a usable face.
- System performs quality checks.
- System creates a secure face template/embedding.
- Face enrollment status is stored.
- Re-enrollment must be controlled and audited.

## FR-05 Face Verification
- Attendance attempts require face verification.
- Live captured face is compared with the registered template.
- Verification returns pass/fail and an appropriate confidence/similarity result.
- Failed verification does not create a valid attendance record.

## FR-06 Liveness
- Attendance verification should include liveness/anti-spoofing.
- Photo/screen/replay attacks should be mitigated as far as the selected technology allows.
- Liveness failures are logged as failed verification attempts.

## FR-07 Geolocation
- Admin can configure one or more attendance locations.
- Each location has latitude, longitude, and allowed radius.
- Browser location is obtained during attendance.
- Distance from the configured location is calculated.
- Attendance outside the allowed radius is rejected.
- GPS permission denial or unusable accuracy is handled gracefully.

## FR-08 Attendance
- OJT Trainee can Time In.
- OJT Trainee can Time Out.
- Both events use required verification.
- Duplicate or invalid events are rejected.
- Attendance stores timestamp and verification evidence.
- Rendered hours are calculated according to configured rules.

## FR-09 Daily Logs
OJT Trainees can submit:
- Date
- Activities
- Learnings
- Challenges
- Other configured fields

Admins can review, approve, reject, and comment.

## FR-10 OJT Progress
- System tracks required hours.
- System calculates rendered hours.
- System calculates progress percentage.
- System identifies remaining hours.
- OJT can transition to Completed.

## FR-11 Evaluation
- Admin can evaluate OJT trainees.
- Evaluation contains ratings/comments as configured.
- OJT Trainee can view released evaluation results.

## FR-12 Reports
Admin reports:
- Attendance
- Absences/lateness
- Rendered hours
- OJT progress
- Daily logs
- Completion

Super Admin can view system-wide reports.

## FR-13 Audit Logs
The system records important actions including:
- Login/security events
- Application approval/rejection
- Document review
- Face enrollment
- Attendance attempts
- Verification failures
- Configuration changes
- Administrative actions

## Non-Functional Requirements

### Security
- HTTPS
- Password hashing
- RBAC
- Server-side authorization
- Input validation
- Secure file handling
- Rate limiting
- Audit logging

### Privacy
- Minimize biometric access
- Minimize location collection
- Define retention/deletion rules
- Provide appropriate privacy notice/consent flow
- Do not expose biometric templates to normal users

### Reliability
- Attendance writes should be transactional.
- Verification failures should not corrupt attendance history.
- Backups should be configured for production.

### Maintainability
- Modular services
- Clear API contracts
- Automated tests for core business rules
- Environment-specific configuration
