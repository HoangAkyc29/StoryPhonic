<template>
  <div class="novel-status-display">
    <!-- Processing/Pending State -->
    <div v-if="status === 'pending' || status === 'processing'">
      <div class="status-icon-container">
        <div class="spinner"></div>
      </div>
      <h2>{{ novel?.name }}</h2>
      <p>Created: {{ novel?.created_at ? new Date(novel.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '' }}</p>
      <p class="status-message processing-message">Your audiobook is being processed. Please wait...</p>
    </div>

    <!-- Completed State -->
    <div v-else-if="status === 'completed'">
      <div class="status-icon-container">
        <div class="completion-icon">✔</div>
      </div>
      <h2>{{ novel?.name }}</h2>
      <p>Created: {{ novel?.created_at ? new Date(novel.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '' }}</p>
      <p class="status-message completion-message">Your audiobook is ready!</p>
    </div>

    <!-- Optional: Default state for other statuses (e.g., error) -->
    <!-- <div v-else>
         <p>Status: {{ status }}</p>
         <p>An unexpected status occurred.</p>
    </div> -->
  </div>
</template>

<script setup lang="ts">
// Remove currentStep prop and steps array as they are no longer displayed
defineProps<{ status: string, novel?: any }>()
// const steps = [...] // Removed
</script>

<style scoped>
/* Main container styling - shared */
.novel-status-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 350px;
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 2rem;
  margin-top: 2rem;
  text-align: center; /* Center text content */
}

/* Container for the icon/spinner */
.status-icon-container {
  margin-bottom: 1.5rem;
}

/* Spinner styles (for pending/processing) */
.spinner {
  width: 48px;
  height: 48px;
  border: 5px solid #e0e7ef;
  border-top: 5px solid #0ea5e9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto; /* Center the spinner */
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Completion icon styles (for completed) */
.completion-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #10b981; /* A nice success green */
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem; /* Make the tick mark prominent */
  font-weight: 700;
  line-height: 1; /* Adjust line height for vertical centering */
  margin: 0 auto; /* Center the icon */
}

/* Shared message styling */
.status-message {
  font-size: 1.1rem;
  margin: 1rem 0 0 0; /* Adjust margin */
}

/* Specific message colors */
.processing-message {
  color: #0ea5e9; /* Blue */
}

.completion-message {
  color: #10b981; /* Green */
}

/* --- Removed Styles --- */
/* Removed styles for:
  .pipeline-steps
  .step-row
  .step-circle
  .step-info
  .step-title
  .step-status
*/
</style>