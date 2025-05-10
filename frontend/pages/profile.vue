<template>
  <div class="profile-root">
    <div class="profile-container">
      <div class="profile-card">
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <img :src="user?.avatar" :alt="user?.first_name + ' ' + user?.last_name" class="avatar" />
            <input type="file" ref="avatarInput" accept="image/*" class="hidden" @change="handleAvatarChange" />
            <button class="avatar-btn" @click="triggerAvatarInput" title="Change avatar">
              <Icon name="heroicons:camera" size="22" />
            </button>
          </div>
          <div class="user-info">
            <h2 class="user-name">{{ user?.first_name + ' ' + user?.last_name }}</h2>
            <div class="user-email">{{ user?.email }}</div>
          </div>
        </div>
        <div class="profile-stats">
          <!-- Nếu muốn hiển thị các stat, cần có dữ liệu từ backend. Nếu không có thì ẩn đi -->
        </div>
      </div>
      <div class="settings-card">
        <h3 class="settings-title">Account Settings</h3>
        <form @submit.prevent="handleUpdateProfile" class="settings-form">
          <div class="form-group">
            <label for="first_name">First Name</label>
            <input type="text" id="first_name" v-model="profileData.first_name" class="form-input" :disabled="loading" />
          </div>
          <div class="form-group">
            <label for="last_name">Last Name</label>
            <input type="text" id="last_name" v-model="profileData.last_name" class="form-input" :disabled="loading" />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" :value="user?.email" class="form-input" disabled />
          </div>
          <div class="form-actions">
            <button type="submit" class="save-btn" :disabled="loading">
              {{ loading ? 'Saving...' : 'Save Changes' }}
            </button>
            <button type="button" class="change-password-btn" @click="showChangePassword = true" :disabled="loading">
              Change Password
            </button>
          </div>
        </form>
      </div>
    </div>
    <div v-if="showChangePassword" class="modal-overlay">
      <div class="modal-content">
        <h3>Change Password</h3>
        <form @submit.prevent="handleChangePassword" class="password-form">
          <div class="form-group">
            <label for="current_password">Current Password</label>
            <input type="password" id="current_password" v-model="passwordForm.current_password" class="form-input" :disabled="loading" />
          </div>
          <div class="form-group">
            <label for="new_password">New Password</label>
            <input type="password" id="new_password" v-model="passwordForm.new_password" class="form-input" :disabled="loading" />
          </div>
          <div class="form-group">
            <label for="confirm_password">Confirm New Password</label>
            <input type="password" id="confirm_password" v-model="passwordForm.confirm_password" class="form-input" :disabled="loading" />
          </div>
          <div class="form-actions">
            <button type="submit" class="save-btn" :disabled="loading">
              {{ loading ? 'Updating...' : 'Update Password' }}
            </button>
            <button type="button" class="cancel-btn" @click="showChangePassword = false" :disabled="loading">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import { useProfile } from '~/composables/useProfile'

const { user } = useAuth()
const { loading, updateProfile, changePassword, updateAvatar } = useProfile()

const showChangePassword = ref(false)
const avatarInput = ref<HTMLInputElement | null>(null)

const profileData = ref({
  first_name: user.value?.first_name || '',
  last_name: user.value?.last_name || '',
  email: user.value?.email || ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

onMounted(() => {
  if (user.value) {
    profileData.value = {
      first_name: user.value.first_name,
      last_name: user.value.last_name,
      email: user.value.email
    }
  }
})

const handleUpdateProfile = async () => {
  try {
    await updateProfile(profileData.value)
    // Show success message
  } catch (e) {
    // Show error message
    console.error(e)
  }
}

const handleChangePassword = async () => {
  try {
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
      alert('New passwords do not match')
      return
    }
    await changePassword({
      current_password: passwordForm.value.current_password,
      new_password: passwordForm.value.new_password,
      confirm_password: passwordForm.value.confirm_password
    })
    showChangePassword.value = false
    // Show success message
  } catch (e) {
    // Show error message
    console.error(e)
  }
}

const triggerAvatarInput = () => {
  avatarInput.value?.click()
}

const handleAvatarChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    try {
      await updateAvatar(input.files[0])
      // Show success message
    } catch (e) {
      // Show error message
      console.error(e)
    }
  }
}
</script>

<style scoped>
.profile-root {
  min-height: 100vh;
  background: linear-gradient(120deg, #e0f7fa 0%, #f8fbff 100%);
  padding: 2.5rem 0 2rem 0;
}
.profile-container {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 2.5rem;
  justify-content: center;
}
.profile-card {
  background: #fff;
  border-radius: 1.2rem;
  box-shadow: 0 4px 24px rgba(14,165,233,0.10);
  padding: 2.5rem 2.2rem 2rem 2.2rem;
  min-width: 320px;
  max-width: 350px;
  flex: 1 1 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  width: 100%;
}
.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 0.5rem;
}
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #bae6fd;
  background: #e0f7fa;
  box-shadow: 0 2px 12px rgba(56,189,248,0.10);
}
.avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(90deg, #0ea5e9 60%, #38bdf8 100%);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(14,165,233,0.13);
  transition: background 0.2s;
}
.avatar-btn:hover {
  background: linear-gradient(90deg, #38bdf8 0%, #0ea5e9 100%);
}
.user-info {
  text-align: center;
}
.user-name {
  font-size: 1.35rem;
  font-weight: 700;
  color: #0ea5e9;
  margin-bottom: 0.2rem;
}
.user-email {
  color: #222;
  font-size: 1.05rem;
  font-weight: 500;
  letter-spacing: 0.1px;
}
.profile-stats {
  display: flex;
  gap: 1.1rem;
  margin-top: 2.2rem;
  width: 100%;
  justify-content: center;
}
.stat-card {
  background: #e0f7fa;
  border-radius: 0.9rem;
  padding: 1.1rem 1.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 90px;
  box-shadow: 0 2px 8px rgba(56,189,248,0.08);
}
.stat-icon {
  color: #0ea5e9;
  font-size: 1.5rem;
  margin-bottom: 0.3rem;
}
.stat-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: #0369a1;
}
.stat-label {
  font-size: 0.85rem;
  color: #38bdf8;
  margin-top: 0.1rem;
}
.settings-card {
  background: #fff;
  border-radius: 1.2rem;
  box-shadow: 0 4px 24px rgba(14,165,233,0.10);
  padding: 2.5rem 2.2rem 2rem 2.2rem;
  min-width: 340px;
  max-width: 480px;
  flex: 2 1 340px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.settings-title {
  color: #0ea5e9;
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.form-group label {
  color: #0369a1;
  font-weight: 500;
  font-size: 1rem;
}
.form-input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1.5px solid #e0e7ef;
  border-radius: 0.7rem;
  font-size: 1.05rem;
  background: #f8fafc;
  color: #222;
  transition: border 0.2s, box-shadow 0.2s;
}
.form-input:focus {
  border: 1.5px solid #0ea5e9;
  outline: none;
  box-shadow: 0 2px 8px rgba(14,165,233,0.10);
}
.form-input:disabled {
  background: #f3f4f6;
  color: #aaa;
  cursor: not-allowed;
}
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #222;
  font-size: 1rem;
  cursor: pointer;
}
.form-actions {
  display: flex;
  gap: 1.2rem;
  margin-top: 1.2rem;
}
.save-btn {
  background: linear-gradient(90deg, #0ea5e9 60%, #38bdf8 100%);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 0.7rem 2.2rem;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
  box-shadow: 0 2px 12px rgba(14,165,233,0.10);
}
.save-btn:disabled {
  background: #b6e0fa;
  cursor: not-allowed;
}
.save-btn:hover:not(:disabled) {
  background: linear-gradient(90deg, #38bdf8 0%, #0ea5e9 100%);
}
.change-password-btn {
  background: #e0f2fe;
  color: #0ea5e9;
  border: none;
  border-radius: 999px;
  padding: 0.7rem 2.2rem;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  box-shadow: 0 2px 12px rgba(14,165,233,0.10);
}
.change-password-btn:disabled {
  background: #f3f4f6;
  color: #aaa;
  cursor: not-allowed;
}
.change-password-btn:hover:not(:disabled) {
  background: #0ea5e9;
  color: #fff;
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(14,165,233,0.13);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}
.modal-content {
  background: #fff;
  border-radius: 1.2rem;
  box-shadow: 0 8px 32px rgba(14,165,233,0.18);
  padding: 2.5rem 2.2rem 2rem 2.2rem;
  min-width: 320px;
  max-width: 95vw;
  position: relative;
  text-align: center;
}
.modal-content h3 {
  color: #0ea5e9;
  margin-bottom: 1.5rem;
}
.cancel-btn {
  background: #f3f4f6;
  color: #222;
  border: none;
  border-radius: 999px;
  padding: 0.7rem 2.2rem;
  font-weight: 700;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  margin-left: 0.5rem;
}
.cancel-btn:disabled {
  background: #e0e7ef;
  color: #aaa;
  cursor: not-allowed;
}
.cancel-btn:hover:not(:disabled) {
  background: #bae6fd;
  color: #0ea5e9;
}
.hidden {
  display: none;
}
@media (max-width: 900px) {
  .profile-container {
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }
  .profile-card, .settings-card {
    max-width: 100%;
    min-width: 0;
  }
}
</style> 