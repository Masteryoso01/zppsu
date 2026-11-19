const map = {
  Approved: 'success', Active: 'success', 'On Time': 'success', Completed: 'success', Enrolled: 'success', Released: 'success', Ongoing: 'primary', Success: 'success',
  Pending: 'warning', Late: 'warning', 'Pending Review': 'warning', 'Not Started': 'neutral',
  Rejected: 'danger', Suspended: 'danger', Failed: 'danger', 'Not Enrolled': 'neutral', Inactive: 'neutral',
}

export function statusTone(status) {
  return map[status] || 'neutral'
}
