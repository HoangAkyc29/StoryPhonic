<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-left">
        <span class="brand">Story Phonic</span>
        <span class="slogan">Turn your book into a multicast AI audiobook in minutes.</span>
      </div>
      <div class="footer-links">
        <NuxtLink to="/about">About</NuxtLink>
        <NuxtLink to="/contact">Contact</NuxtLink>
        <NuxtLink to="/privacy">Privacy</NuxtLink>
        <NuxtLink to="/terms">Terms</NuxtLink>
        <a href="https://github.com/" target="_blank">GitHub</a>
      </div>
      <div class="footer-social">
        <a href="#" title="Facebook"><Icon name="mdi:facebook" /></a>
        <a href="#" title="Twitter"><Icon name="mdi:twitter" /></a>
        <a href="#" title="YouTube"><Icon name="mdi:youtube" /></a>
      </div>
    </div>
    <div class="footer-bottom">
      &copy; {{ new Date().getFullYear() }} Story Phonic. All rights reserved.
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.footer {
  background: #18181b;
  color: #fff;
  padding: 2rem 0 1rem 0;
  border-top: 1px solid #222;
  margin-top: auto;
}
.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
  padding: 0 2rem;
  gap: 1.5rem;
}
.footer-left {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.brand {
  font-size: 1.2rem;
  font-weight: bold;
  color: #38bdf8;
}
.slogan {
  font-size: 1rem;
  color: #bdbdbd;
}
.footer-links {
  display: flex;
  gap: 1.2rem;
}
.footer-links a {
  color: #38bdf8;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
.footer-links a:hover {
  color: #0ea5e9;
  text-decoration: underline;
}
.footer-social {
  display: flex;
  gap: 1rem;
}
.footer-social a {
  color: #fff;
  font-size: 1.5rem;
  transition: color 0.2s;
}
.footer-social a:hover {
  color: #38bdf8;
}
.footer-bottom {
  text-align: center;
  color: #bdbdbd;
  font-size: 0.95rem;
  margin-top: 1.5rem;
}
</style> 