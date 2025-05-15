import { auth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware(async (to, _from) => {
  // Các route public không cần đăng nhập
  const publicPages = ['/', '/login', '/signup', '/pricing', '/features']
  const { user, checkAuth } = auth

  if (import.meta.client) {
    await checkAuth()
    const token = localStorage.getItem('token')

    // Nếu đã login mà vào trang login thì chuyển về dashboard
    if (to.path === '/login' && token && user.value) {
      return navigateTo('/dashboard')
    }

    // Nếu vào trang private mà không có token hoặc user thì về login
    if (!publicPages.includes(to.path) && (!token || !user.value)) {
      return navigateTo('/login')
    }
  }
}) 