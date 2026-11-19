import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/',
    component: () => import('../layouts/AuthLayout.vue'),
    meta: { guestOnly: true },
    children: [
      { path: 'login', name: 'login', component: () => import('../views/auth/LoginView.vue') },
      { path: 'register', name: 'register', meta: { wide: true }, component: () => import('../views/auth/RegisterView.vue') },
      { path: 'forgot-password', name: 'forgot-password', component: () => import('../views/auth/ForgotPasswordView.vue') },
    ],
  },
  {
    path: '/intern',
    component: () => import('../layouts/AppLayout.vue'),
    meta: { requiresAuth: true, role: 'intern' },
    children: [
      { path: '', redirect: '/intern/dashboard' },
      { path: 'dashboard', name: 'intern-dashboard', component: () => import('../views/intern/DashboardView.vue') },
      { path: 'profile', name: 'intern-profile', component: () => import('../views/intern/ProfileView.vue') },
      { path: 'attendance', name: 'intern-attendance', component: () => import('../views/intern/AttendanceView.vue') },
      { path: 'daily-logs', name: 'intern-daily-logs', component: () => import('../views/intern/DailyLogsView.vue') },
      { path: 'progress', name: 'intern-progress', component: () => import('../views/intern/ProgressView.vue') },
      { path: 'evaluation', name: 'intern-evaluation', component: () => import('../views/intern/EvaluationView.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('../layouts/AppLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: () => import('../views/admin/DashboardView.vue') },
      { path: 'interns', name: 'admin-interns', component: () => import('../views/admin/InternsView.vue') },
      { path: 'interns/:id', name: 'admin-intern-detail', component: () => import('../views/admin/InternDetailView.vue') },
      { path: 'attendance', name: 'admin-attendance', component: () => import('../views/admin/AttendanceReviewView.vue') },
      { path: 'daily-logs', name: 'admin-daily-logs', component: () => import('../views/admin/DailyLogsReviewView.vue') },
      { path: 'evaluations', name: 'admin-evaluations', component: () => import('../views/admin/EvaluationsView.vue') },
      { path: 'locations', name: 'admin-locations', component: () => import('../views/admin/LocationsView.vue') },
      { path: 'reports', name: 'admin-reports', component: () => import('../views/admin/ReportsView.vue') },
    ],
  },
  {
    path: '/super-admin',
    component: () => import('../layouts/AppLayout.vue'),
    meta: { requiresAuth: true, role: 'super-admin' },
    children: [
      { path: '', redirect: '/super-admin/dashboard' },
      { path: 'dashboard', name: 'super-admin-dashboard', component: () => import('../views/super-admin/DashboardView.vue') },
      { path: 'applications', name: 'super-admin-applications', component: () => import('../views/super-admin/ApplicationsView.vue') },
      { path: 'organizations/:id', name: 'super-admin-organization-detail', component: () => import('../views/super-admin/OrganizationDetailView.vue') },
      { path: 'organizations', name: 'super-admin-organizations', component: () => import('../views/super-admin/OrganizationsView.vue') },
      { path: 'admins', name: 'super-admin-admins', component: () => import('../views/super-admin/AdminsView.vue') },
      { path: 'reports', name: 'super-admin-reports', component: () => import('../views/super-admin/ReportsView.vue') },
      { path: 'audit-logs', name: 'super-admin-audit-logs', component: () => import('../views/super-admin/AuditLogsView.vue') },
      { path: 'settings', name: 'super-admin-settings', component: () => import('../views/super-admin/SettingsView.vue') },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return auth.homePath
  }
  if (to.meta.role && auth.role !== to.meta.role) {
    return auth.homePath
  }
  return true
})

export default router
