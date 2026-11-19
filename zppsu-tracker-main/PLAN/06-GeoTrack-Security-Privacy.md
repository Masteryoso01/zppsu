# GeoTrack — Security and Privacy Plan

## Sensitive Data
GeoTrack handles:
- Personal information
- Student IDs
- OJT documents
- Face/biometric templates
- Location information
- Attendance history

## Security Controls
1. HTTPS everywhere.
2. Strong password hashing.
3. Role-based access control.
4. Organization-level authorization.
5. Server-side validation.
6. Secure file upload validation.
7. Secure document storage.
8. Restricted biometric access.
9. Rate limiting.
10. Audit logging.
11. Secrets stored in environment/secret management, never source control.
12. Database backups and restore testing.

## Biometric Data
- Prefer storing a face template/embedding reference rather than raw images when technically appropriate.
- Restrict who can access biometric information.
- Do not expose face templates through normal API responses.
- Define enrollment, re-enrollment, retention, and deletion procedures.
- Log administrative biometric actions.

## Location Data
- Collect only when needed.
- Use location for Time In/Out validation.
- Avoid continuous tracking unless a separate requirement and appropriate privacy basis exists.
- Define retention for attendance location evidence.

## Documents
- Validate MIME/type and file size.
- Store outside public web root or behind authorized download endpoints.
- Do not expose predictable file URLs.
- Scan uploads if production infrastructure supports it.

## Authorization
Every protected request should validate:
- authenticated user
- role
- organization ownership/access
- resource ownership
- action permission

## Audit
Record security-sensitive actions without storing unnecessary sensitive payloads.

## Privacy Documentation
The final production system should have:
- Privacy notice
- Appropriate consent/legal basis documentation
- Retention schedule
- Deletion/revocation procedure
- Data access procedure
