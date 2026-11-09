<script setup>
defineProps({ label: String, value: [Number, String], icon: String })
</script>

<template>
  <div class="stat-card">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-row">
      <span class="stat-value">{{ value }}</span>
      <span class="stat-icon">{{ icon }}</span>
    </div>
  </div>
</template>
