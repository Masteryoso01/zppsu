# GeoTrack — Data Model

## Core Tables

### users
- id
- name
- email
- password_hash
- role
- status
- created_at
- updated_at

### organizations
- id
- name
- address
- status
- created_at
- updated_at

### intern_profiles
- id
- user_id
- student_id_number
- school
- course
- year_level
- contact_number
- address
- created_at
- updated_at

### internship_programs
- id
- organization_id
- name
- description
- required_hours
- status
- created_at
- updated_at

### internships
- id
- intern_id
- program_id
- start_date
- end_date
- required_hours
- status
- created_at
- updated_at

### locations
- id
- organization_id
- name
- latitude
- longitude
- allowed_radius
- status
- created_at
- updated_at

### requirements
- id
- organization_id
- program_id
- name
- description
- required
- allowed_file_types
- max_file_size
- status

### documents
- id
- intern_id
- requirement_id
- file_path
- status
- reviewed_by
- reviewed_at
- rejection_reason
- created_at
- updated_at

### face_profiles
- id
- intern_id
- face_template_reference
- status
- enrolled_at
- updated_at

### attendance
- id
- intern_id
- internship_id
- location_id
- type
- timestamp
- latitude
- longitude
- distance
- status
- created_at

### attendance_verifications
- id
- attendance_id
- face_verified
- liveness_verified
- gps_verified
- face_score
- gps_accuracy
- failure_reason
- created_at

### daily_logs
- id
- intern_id
- internship_id
- date
- activities
- learnings
- challenges
- status
- reviewed_by
- reviewed_at
- reviewer_comment
- created_at
- updated_at

### evaluations
- id
- intern_id
- internship_id
- evaluator_id
- rating
- comments
- status
- created_at
- updated_at

### audit_logs
- id
- user_id
- action
- resource_type
- resource_id
- result
- metadata
- created_at

## Relationships

```text
organizations
  ├── admins/users
  ├── locations
  ├── requirements
  └── internship_programs
          |
          v
      internships
          |
          v
        intern
          |
    +-----+-----+--------+---------+
    |           |        |         |
 documents  face_profile attendance daily_logs
                                      |
                                  evaluations
```

## Important Design Decisions
- Keep biometric template storage separate from normal profile data.
- Do not store raw face images unless there is a documented need.
- Use IDs/foreign keys instead of duplicating organization data.
- Add indexes for user_id, intern_id, organization_id, timestamps, and attendance lookup fields.
