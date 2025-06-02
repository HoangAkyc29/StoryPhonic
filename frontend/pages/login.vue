<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'

const { login, loginWithGoogle, loading, error } = useAuth()
const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = async () => {
  if (!email.value || !password.value) {
    error.value = 'Please fill in all fields'
    return
  }
  try {
    const loggedInUser = await login({ email: email.value, password: password.value })
    if (loggedInUser) {
      router.push('/dashboard')
    }
  } catch (e) {
    // Có thể hiển thị error ở đây
    console.error(e)
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-box">
      <h1>Login</h1>
      <form @submit.prevent="handleLogin">
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit" :disabled="loading">Login</button>
        <div v-if="error" style="color:red">{{ error }}</div>
      </form>

      <div class="divider">
        <span>or</span>
      </div>
      <button @click="loginWithGoogle" :disabled="loading" class="google-btn">
        <img src="/g_logo.png" alt="Google Logo" class="google-icon" />
        Sign in with Google
      </button>

      <p class="switch">Don't have an account? <NuxtLink to="/signup">Sign up</NuxtLink></p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}
.auth-box {
  background: #fff;
  padding: 2.5rem 2rem 2rem 2rem;
  border-radius: 1.2rem;
  box-shadow: 0 2px 16px rgba(56,189,248,0.10);
  min-width: 320px;
  text-align: center;
}
.auth-box h1 {
  color: #0ea5e9;
  margin-bottom: 1.5rem;
}
input {
  width: 100%;
  padding: 0.8rem;
  margin-bottom: 1rem;
  border: 1px solid #e0f2fe;
  border-radius: 0.5rem;
  font-size: 1rem;
}
button {
  width: 100%;
  background: #0ea5e9;
  color: #fff;
  padding: 0.8rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover {
  background: #0369a1;
}
.switch {
  margin-top: 1rem;
  color: #555;
}
.switch a {
  color: #0ea5e9;
  text-decoration: none;
}
.switch a:hover {
  text-decoration: underline;
}
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1rem 0;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0f2fe;
}
.divider span {
  padding: 0 1rem;
  color: #555;
  font-size: 0.9rem;
}
.google-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  color: #555;
  border: 1px solid #dadce0;
  margin-top: 1rem;
  padding: 0.8rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.google-btn:hover {
  background: #f8f9fa;
}
.google-icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-right: 0.5rem;
}
</style> 