<template>
  <div class="stories-page">
    <h1 class="page-title">My Stories</h1>

    <div class="stories-grid">
      <div v-for="story in stories" :key="story.id" class="story-card">
        <img :src="story.coverImage" :alt="story.title" class="story-cover">
        <div class="story-info">
          <h3>{{ story.title }}</h3>
          <p>{{ story.description }}</p>
          <div class="story-meta">
            <span class="level">
              <Icon name="heroicons:academic-cap" />
              Level: {{ story.level }}
            </span>
            <span class="duration">
              <Icon name="heroicons:clock" />
              {{ story.duration }} minutes
            </span>
          </div>
          <div class="story-progress">
            <div class="progress-bar">
              <div class="progress" :style="{ width: story.progress + '%' }"></div>
            </div>
            <span>{{ story.progress }}% completed</span>
          </div>
          <button class="continue-btn" @click="continueStory(story.id)">
            Continue Learning
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'dashboard'
})

// Mock data - will be replaced with real data from API
const stories = ref([
  {
    id: 1,
    title: 'Little Red Riding Hood',
    description: 'A fairy tale about courage and wisdom',
    coverImage: '/images/stories/little-red-riding-hood.jpg',
    level: 'Beginner',
    duration: 15,
    progress: 75
  },
  {
    id: 2,
    title: 'The Three Little Pigs',
    description: 'A lesson about hard work and perseverance',
    coverImage: '/images/stories/three-little-pigs.jpg',
    level: 'Beginner',
    duration: 20,
    progress: 45
  },
  {
    id: 3,
    title: 'The Jungle Book',
    description: 'The adventures of a boy raised by animals',
    coverImage: '/images/stories/jungle-book.jpg',
    level: 'Intermediate',
    duration: 25,
    progress: 90
  }
])

const continueStory = (storyId: number) => {
  // Handle continue learning
  navigateTo(`/dashboard/stories/${storyId}`)
}
</script>

<style scoped>
.stories-page {
  padding: 1rem;
  /* background: transparent; */
}

.page-title {
  margin-bottom: 2rem;
  color: #333;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.story-card {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.story-cover {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.story-info {
  padding: 1.5rem;
}

.story-info h3 {
  margin: 0 0 0.5rem;
  color: #333;
  font-size: 1.25rem;
}

.story-info p {
  margin: 0 0 1rem;
  color: #666;
  font-size: 0.9rem;
}

.story-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.story-meta span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.story-meta .icon {
  width: 1rem;
  height: 1rem;
}

.story-progress {
  margin-bottom: 1rem;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress {
  height: 100%;
  background: #4CAF50;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.story-progress span {
  font-size: 0.8rem;
  color: #666;
}

.continue-btn {
  width: 100%;
  padding: 0.75rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.continue-btn:hover {
  background: #43A047;
}
</style> 