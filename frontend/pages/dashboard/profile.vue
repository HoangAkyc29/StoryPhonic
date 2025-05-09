<template>
  <div class="profile-page">
    <h1 class="page-title">Profile</h1>

    <div class="profile-content">
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-container">
            <img :src="user?.avatar" :alt="user?.name" class="avatar">
            <input 
              type="file" 
              ref="avatarInput" 
              accept="image/*" 
              class="hidden" 
              @change="handleAvatarChange"
            >
            <button class="change-avatar-btn" @click="triggerAvatarInput">
              <Icon name="heroicons:camera" />
            </button>
          </div>
          <h2>{{ user?.name }}</h2>
          <p class="user-email">{{ user?.email }}</p>
        </div>

        <div class="profile-stats">
          <div class="stat-item">
            <Icon name="heroicons:academic-cap" />
            <div class="stat-info">
              <span class="stat-value">{{ user?.level }}</span>
              <span class="stat-label">Current Level</span>
            </div>
          </div>
          <div class="stat-item">
            <Icon name="heroicons:star" />
            <div class="stat-info">
              <span class="stat-value">{{ user?.points }}</span>
              <span class="stat-label">Total Points</span>
            </div>
          </div>
          <div class="stat-item">
            <Icon name="heroicons:clock" />
            <div class="stat-info">
              <span class="stat-value">{{ user?.totalTime }}</span>
              <span class="stat-label">Learning Time</span>
            </div>
          </div>
        </div>
      </div>

      <div class="settings-card">
        <h3>Account Settings</h3>
        <form @submit.prevent="handleUpdateProfile" class="settings-form">
          <div class="form-group">
            <label for="name">Full Name</label>
            <input 
              type="text" 
              id="name" 
              v-model="profileData.name"
              class="form-input"
              :disabled="loading"
            >
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              :value="user?.email"
              class="form-input"
              disabled
            >
          </div>

          <div class="form-group">
            <label for="language">Preferred Language</label>
            <select 
              id="language" 
              v-model="profileData.language"
              class="form-input"
              :disabled="loading"
            >
              <option value="en">English</option>
              <option value="vi">Vietnamese</option>
            </select>
          </div>

          <div class="form-group">
            <label for="notifications">Notifications</label>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="profileData.notifications.email"
                  :disabled="loading"
                >
                Email Notifications
              </label>
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="profileData.notifications.reminders"
                  :disabled="loading"
                >
                Daily Reminders
              </label>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="save-btn" :disabled="loading">
              {{ loading ? 'Saving...' : 'Save Changes' }}
            </button>
            <button 
              type="button" 
              class="change-password-btn" 
              @click="showChangePassword = true"
              :disabled="loading"
            >
              Change Password
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showChangePassword" class="modal">
      <div class="modal-content">
        <h3>Change Password</h3>
        <form @submit.prevent="handleChangePassword" class="password-form">
          <div class="form-group">
            <label for="currentPassword">Current Password</label>
            <input 
              type="password" 
              id="currentPassword" 
              v-model="passwordForm.current"
              class="form-input"
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="newPassword">New Password</label>
            <input 
              type="password" 
              id="newPassword" 
              v-model="passwordForm.new"
              class="form-input"
              :disabled="loading"
            >
          </div>
          <div class="form-group">
            <label for="confirmPassword">Confirm New Password</label>
            <input 
              type="password" 
              id="confirmPassword" 
              v-model="passwordForm.confirm"
              class="form-input"
              :disabled="loading"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="save-btn" :disabled="loading">
              {{ loading ? 'Updating...' : 'Update Password' }}
            </button>
            <button 
              type="button" 
              class="cancel-btn" 
              @click="showChangePassword = false"
              :disabled="loading"
            >
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
  name: user.value?.name || '',
  language: user.value?.language || 'en',
  notifications: {
    email: user.value?.notifications.email || false,
    reminders: user.value?.notifications.reminders || false
  }
})

const passwordForm = ref({
  current: '',
  new: '',
  confirm: ''
})

onMounted(() => {
  if (user.value) {
    profileData.value = {
      name: user.value.name,
      language: user.value.language,
      notifications: { ...user.value.notifications }
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
    if (passwordForm.value.new !== passwordForm.value.confirm) {
      alert('New passwords do not match')
      return
    }
    await changePassword({
      currentPassword: passwordForm.value.current,
      newPassword: passwordForm.value.new,
      confirmPassword: passwordForm.value.confirm
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
.profile-page {
  padding: 1rem;
}

.page-title {
  margin-bottom: 2rem;
  color: #333;
}

.profile-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
}

.profile-card {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.profile-header {
  text-align: center;
  margin-bottom: 2rem;
}

.avatar-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 1rem;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-email {
  color: #666;
  margin-top: 0.5rem;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #f8f8f8;
  border-radius: 0.5rem;
}

.stat-item .icon {
  width: 24px;
  height: 24px;
  color: #4CAF50;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
}

.settings-card {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.settings-card h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  font-size: 1rem;
}

.form-input:disabled {
  background: #f5f5f5;
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
  gap: 0.5rem;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.save-btn {
  padding: 0.75rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
}

.change-password-btn {
  padding: 0.75rem 1.5rem;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  width: 100%;
  max-width: 400px;
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
}

.hidden {
  display: none;
}

.save-btn:disabled,
.change-password-btn:disabled,
.cancel-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style> 