# GeoTrack — Attendance Verification Specification

## Goal
Create a trustworthy Time In/Time Out process using identity, liveness, location, and schedule validation.

## Verification Pipeline

```text
User selects Time In/Out
        |
        v
Camera Permission
        |
        v
Face Capture
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
GPS Acquisition
        |
        v
GPS Radius Validation
        |
        v
Schedule/Attendance Rule Validation
        |
        v
AttendanceService
        |
        +--> Save attendance
        +--> Save verification result
        +--> Create audit event
```

## Failure Examples

### No face
Reject with a user-friendly message.

### Multiple faces
Reject or require exactly one detected face.

### Face mismatch
Reject and do not create a valid attendance event.

### Liveness failure
Reject and log the failed verification.

### GPS unavailable
Do not silently approve. Tell the user that location verification is required.

### Outside radius
Reject with the configured reason.

## Anti-Abuse Considerations
- Rate limit verification attempts.
- Record failed attempts.
- Consider device/session metadata where appropriate.
- Consider GPS accuracy thresholds.
- Do not rely on frontend-only checks.
- Treat liveness as a security control, not as a cosmetic camera step.

## Privacy
Location should be collected for attendance verification rather than continuous tracking by default.

Biometric templates must have restricted access and an explicit retention/deletion policy.
