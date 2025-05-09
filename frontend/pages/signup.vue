<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '~/composables/useAuth'

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const { register, error, loading } = useAuth()

const handleRegister = async () => {
  try {
    await register({
      username: email.value,
      email: email.value,
      password: password.value,
      confirmPassword: confirmPassword.value
    })
    window.location.href = '/dashboard'
  } catch (e) {
    // Có thể hiển thị error ở đây
    console.error(e)
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-box">
      <h1>Sign up</h1>
      <form @submit.prevent="handleRegister">
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <input v-model="confirmPassword" type="password" placeholder="Confirm Password" required />
        <button type="submit" :disabled="loading">Sign up</button>
        <div v-if="error" style="color:red">{{ error }}</div>
      </form>
      <p class="switch">Already have an account? <NuxtLink to="/login">Login</NuxtLink></p>
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
</style> 