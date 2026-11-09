<script setup>
import { ref } from 'vue'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppTopbar from '../components/layout/AppTopbar.vue'
import { auth } from '../stores/auth'

const open = ref(true)

const items = [
  { label: 'Dashboard', to: '/admin/dashboard', icon: '▦' },
  { label: 'Treks', to: '/admin/treks', icon: '⛰' },
  { label: 'Trekking Staff', to: '/admin/staff', icon: '🧭' },
  { label: 'Users (Trekkers)', to: '/admin/users', icon: '👥' },
  { label: 'Bookings', to: '/admin/bookings', icon: '📅' },
  { label: 'Search', to: '/admin/search', icon: '🔍' },
  { label: 'Reports', to: '/admin/reports', icon: '📊' },
  { label: 'Settings', to: '/admin/settings', icon: '⚙' },
]
</script>

<template>
  <div class="app-shell">
    <AppTopbar :user-name="auth.state.user?.name || 'Admin'" @toggle-sidebar="open = !open" />
    <div class="app-body">
      <AppSidebar v-if="open" :items="items" />
      <main class="content"><RouterView /></main>
    </div>
  </div>
</template>
