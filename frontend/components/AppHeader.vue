<template>
  <header class="header">
    <nav class="nav">
      <div class="logo-title">
        <NuxtLink to="/" class="logo-link">
          <img src="/logo-storyphonic.svg" alt="Story Phonic Logo" class="logo" />
          <span class="brand">Story Phonic</span>
        </NuxtLink>
      </div>
      <ul class="menu">
        <li><NuxtLink to="#features" :aria-current="$route.hash === '#features' ? 'page' : null">Features</NuxtLink></li>
        <li><NuxtLink to="/pricing" :aria-current="$route.path === '/pricing' ? 'page' : null">Pricing</NuxtLink></li>
        <li v-if="user"><NuxtLink to="/dashboard" :aria-current="$route.path.startsWith('/dashboard') && $route.path === '/dashboard' ? 'page' : null">My Projects</NuxtLink></li>
        <li v-if="user"><NuxtLink to="/statistics" :aria-current="$route.path === '/statistics' ? 'page' : null">Statistics</NuxtLink></li>
      </ul>
      <div class="auth">
        <button v-if="user" class="logout-btn" @click="handleLogout">Log out</button>
        <NuxtLink v-if="!user" to="/login" class="login">Login</NuxtLink>
        <NuxtLink v-if="!user" to="/signup" class="signup">Sign up</NuxtLink>
        <NuxtLink v-if="user" to="/profile" class="profile-btn">
          <Icon name="heroicons:user-circle" size="28" />
        </NuxtLink>
      </div>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { auth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'

const { user, logout } = auth
const router = useRouter()

const handleLogout = () => {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.header {
  background: #fff;
  border-bottom: 1px solid #e0f2fe;
  padding: 0.5rem 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
}

.logo-title {
  display: flex;
  align-items: center;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo {
  width: 36px;
  height: 36px;
}

.brand {
  font-size: 1.4rem;
  font-weight: bold;
  color: #0ea5e9;
  letter-spacing: 1px;
}

.menu {
  display: flex;
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu li a {
  color: #222;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.2s;
}

.menu li a:hover {
  color: #0ea5e9;
}

.menu .router-link-active,
.menu .router-link-exact-active {
  color: #0ea5e9 !important;
  font-weight: 700;
  pointer-events: none;
  cursor: default;
}

.auth {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.login {
  color: #222;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.2s;
}

.login:hover {
  color: #0ea5e9;
}

.signup {
  background: #0ea5e9;
  color: #fff;
  padding: 0.5rem 1.2rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 1rem;
  text-decoration: none;
  transition: background 0.2s;
}

.signup:hover {
  background: #0369a1;
}

.profile-btn {
  display: flex;
  align-items: center;
  color: #0ea5e9;
  font-size: 1.3rem;
  margin-left: 0.5rem;
  transition: color 0.2s;
}
.profile-btn:hover {
  color: #0369a1;
}

.logout-btn {
  background: none;
  border: none;
  color: #222;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0 0.5rem;
}
.logout-btn:hover {
  color: #0ea5e9;
}
</style> 