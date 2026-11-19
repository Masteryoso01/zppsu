import {
  LayoutDashboard, User, MapPinned, ClipboardList, TrendingUp, Star,
  Building2, Users, ShieldCheck, ScrollText, BarChart3, Settings, UserCheck, Landmark,
} from '@lucide/vue'

export const internNav = [
  { to: '/intern/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/intern/profile', label: 'My Profile', icon: User },
  { to: '/intern/attendance', label: 'Attendance', icon: MapPinned },
  { to: '/intern/daily-logs', label: 'Daily Logs', icon: ClipboardList },
  { to: '/intern/progress', label: 'Progress & Hours', icon: TrendingUp },
  { to: '/intern/evaluation', label: 'Evaluation', icon: Star },
]

export const adminNav = [
  { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/admin/interns', label: 'OJT Trainees', icon: Users },
  { to: '/admin/attendance', label: 'Attendance', icon: MapPinned },
  { to: '/admin/daily-logs', label: 'Daily Logs', icon: ClipboardList },
  { to: '/admin/evaluations', label: 'Evaluations', icon: Star },
  { to: '/admin/locations', label: 'Locations', icon: Landmark },
  { to: '/admin/reports', label: 'Reports', icon: BarChart3 },
]

export const superAdminNav = [
  { to: '/super-admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/super-admin/applications', label: 'Applications & Deployment', icon: UserCheck },
  { to: '/super-admin/organizations', label: 'Organizations', icon: Building2 },
  { to: '/super-admin/admins', label: 'Admin Accounts', icon: ShieldCheck },
  { to: '/super-admin/reports', label: 'System Reports', icon: BarChart3 },
  { to: '/super-admin/audit-logs', label: 'Audit Logs', icon: ScrollText },
  { to: '/super-admin/settings', label: 'Settings', icon: Settings },
]

export const roleLabels = {
  intern: 'OJT Trainee',
  admin: 'Admin',
  'super-admin': 'Super Admin',
}
