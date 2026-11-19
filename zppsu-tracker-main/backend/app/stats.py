"""Attendance statistics (absences, lates, attendance rate) for deployed trainees."""
from datetime import date, timedelta

# A trainee is flagged as a frequent absentee when they have missed at least this many working
# days AND at least this share of the working days since they started.
FREQUENT_MIN_ABSENCES = 3
FREQUENT_MIN_RATE = 0.20
RECENT_DAYS = 30


def _parse(d: str | None) -> date | None:
    try:
        return date.fromisoformat(d) if d else None
    except ValueError:
        return None


def working_days(start: date, end: date) -> list[date]:
    """Mon-Fri days from `start` to `end` inclusive. (Holidays are not tracked yet.)"""
    days, d = [], start
    while d <= end:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def attendance_stats(intern: dict, records: list[dict], today: date) -> dict:
    """Stats for one trainee. Today is excluded from absences because the day is not over yet.

    A working day counts as attended when the trainee has a "Time In" record for it.
    """
    start = _parse(intern.get("startDate"))
    time_ins = [r for r in records if r["internId"] == intern["id"] and r["type"] == "Time In"]
    present_dates = {d for d in (_parse(r["date"]) for r in time_ins) if d}
    last_seen = max((r["date"] for r in time_ins), default=None)

    days = working_days(start, today - timedelta(days=1)) if start else []
    absent = [d for d in days if d not in present_dates]
    present = len(days) - len(absent)
    window_start = today - timedelta(days=RECENT_DAYS)
    absent_recent = [d for d in absent if d >= window_start]
    rate = round(present / len(days) * 100) if days else None
    frequent = len(absent) >= FREQUENT_MIN_ABSENCES and len(absent) / len(days) >= FREQUENT_MIN_RATE

    return {
        "workingDays": len(days),
        "daysPresent": present,
        "daysAbsent": len(absent),
        "absentLast30Days": len(absent_recent),
        "lateCount": sum(1 for r in time_ins if r["status"] == "Late"),
        "attendanceRate": rate,  # percent, None until the trainee has a finished working day
        "lastAttendance": last_seen,
        "recentAbsences": [d.isoformat() for d in sorted(absent, reverse=True)[:5]],
        "frequentAbsent": frequent,
    }
