<template>
  <div class="pricing-page">
    <h1 class="title">Pricing</h1>
    <p class="subtitle">Choose the plan that fits your needs. Start for free, upgrade anytime.</p>
    <div class="plans">
      <div class="plan">
        <h2>Free</h2>
        <div class="price">$0<span>/mo</span></div>
        <ul>
          <li>Up to 1 hour of audio/month</li>
          <li>Basic AI voices</li>
          <li>Standard export</li>
          <li>Email support</li>
        </ul>
        <NuxtLink to="/signup" class="cta">Get Started</NuxtLink>
      </div>
      <div class="plan pro">
        <h2>Pro</h2>
        <div class="price">$19<span>/mo</span></div>
        <ul>
          <li>Up to 20 hours of audio/month</li>
          <li>Premium AI voices</li>
          <li>Multicast voiceover</li>
          <li>Priority support</li>
        </ul>
        <NuxtLink to="/signup" class="cta">Start Pro</NuxtLink>
      </div>
      <div class="plan enterprise">
        <h2>Enterprise</h2>
        <div class="price">Custom</div>
        <ul>
          <li>Unlimited audio hours</li>
          <li>Custom AI voices</li>
          <li>Team collaboration</li>
          <li>Dedicated support</li>
        </ul>
        <NuxtLink to="/signup" class="cta">Contact Sales</NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pricing-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 3rem 1rem 2rem 1rem;
  text-align: center;
}
.title {
  font-size: 2.5rem;
  color: #0ea5e9;
  margin-bottom: 0.5rem;
}
.subtitle {
  color: #555;
  margin-bottom: 2.5rem;
  font-size: 1.2rem;
}
.plans {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  justify-content: center;
}
.plan {
  background: #fff;
  border-radius: 1.2rem;
  box-shadow: 0 2px 16px rgba(56,189,248,0.10);
  padding: 2.2rem 2rem 2rem 2rem;
  width: 290px;
  max-width: 95vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px solid #e0f2fe;
  transition: box-shadow 0.2s, border 0.2s;
}
.plan.pro {
  border: 2px solid #0ea5e9;
  box-shadow: 0 4px 24px rgba(14,165,233,0.12);
}
.plan.enterprise {
  border: 2px dashed #38bdf8;
}
.plan h2 {
  font-size: 1.4rem;
  color: #0ea5e9;
  margin-bottom: 0.5rem;
}
.price {
  font-size: 2.2rem;
  font-weight: bold;
  color: #222;
  margin-bottom: 1.2rem;
}
.price span {
  font-size: 1rem;
  color: #888;
  font-weight: 400;
}
.plan ul {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem 0;
  text-align: left;
}
.plan ul li {
  margin-bottom: 0.7rem;
  color: #333;
  font-size: 1rem;
  padding-left: 1.2rem;
  position: relative;
}
.plan ul li:before {
  content: '✔';
  color: #0ea5e9;
  position: absolute;
  left: 0;
  font-size: 1rem;
}
.cta {
  display: inline-block;
  background: #0ea5e9;
  color: #fff;
  padding: 0.7rem 2rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 1.1rem;
  text-decoration: none;
  transition: background 0.2s;
}
.cta:hover {
  background: #0369a1;
}
</style> 