# GeoTrack — Master Plan

## Project
**GeoTrack: A Geolocation-Based OJT Monitoring and Attendance System**

## Purpose
GeoTrack is a web-based OJT management platform for onboarding OJT trainees, collecting OJT requirements, registering biometric face templates, validating attendance through face verification + liveness + geolocation, tracking rendered hours, reviewing daily logs, and generating reports.

## User Roles
### Super Admin
System-wide administration:
- Manage organizations
- Manage Admin accounts
- View system-wide reports
- Manage system settings
- View audit logs

### Admin
Organization-level management:
- Review OJT trainee applications
- Manage OJT trainees
- Configure OJT programs
- Configure required documents
- Configure attendance locations and radius
- Review attendance and daily logs
- Generate reports
- Evaluate OJT trainees

### OJT Trainee
Personal OJT functions:
- Register
- Complete student profile
- Upload Student ID and requirements
- Register face
- View application status
- Time In / Time Out
- Submit daily logs
- View attendance and rendered hours
- View OJT progress and evaluation

## Core Workflow
Registration -> Documents -> Face Enrollment -> Admin Review -> Approval -> OJT Assignment -> Face/Liveness/GPS Attendance -> Daily Logs -> Hours/Progress -> Evaluation -> Completion.

## Attendance Rule
An attendance event is valid only when required verification checks pass:
1. Face detected
2. Face matches registered OJT trainee
3. Liveness passes
4. GPS is available and within the configured radius
5. Attendance schedule/business rules permit the event

## Main Modules
- Authentication and RBAC
- Organization Management
- OJT Management
- OJT Trainee Onboarding
- Document Management
- Face Enrollment
- Face Verification
- Liveness Detection
- Geolocation Validation
- Attendance
- Daily Logs
- Progress/Hours
- Evaluation
- Reports
- Notifications
- Audit Logs
- Security and Privacy

## Architectural Principle
Use a modular layered architecture:
Frontend -> REST API -> Controllers -> Services -> Repositories/Models -> Database/Storage.

Keep face, liveness, and geolocation logic behind dedicated services so implementations can be replaced without rewriting attendance business logic.

## Proposed Stack
- Frontend: React + Vite + Tailwind CSS
- Backend: PHP/Laravel REST API
- Database: MySQL
- Maps: Leaflet + OpenStreetMap
- Location: Browser Geolocation API
- Face: self-hosted/open-source face verification and liveness components
- Storage: secure object/file storage
- Deployment: separate development, staging/UAT, and production environments

## Important Privacy Rule
GeoTrack should not continuously track OJT trainees by default. Location should be collected for attendance verification events unless a separate, justified requirement exists. Biometric data, student documents, and location data require strict access control, security, retention, and deletion policies.
