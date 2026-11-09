<script setup>
defineProps({ userName: { type: String, default: 'Admin' } })
defineEmits(['toggle-sidebar'])
</script>

<template>
  <header class="topbar">
    <button class="icon-btn" aria-label="Toggle menu" @click="$emit('toggle-sidebar')">☰</button>
    <strong class="topbar-title">Trekking Management Application</strong>
    <span class="topbar-user">👤 {{ userName }} ▾</span>
  </header>
</template>
