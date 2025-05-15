import { auth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware(async (to, _from) => {
  // Các route public không cần đăng nhập
  const publicPages = ['/', '/login', '/signup', '/pricing', '/features']
  if (publicPages.includes(to.path)) return

  const { user, checkAuth } = auth
  if (import.meta.client) {
    await checkAuth()
    if (!user.value) {
      return navigateTo('/login')
    }
  }
}) 