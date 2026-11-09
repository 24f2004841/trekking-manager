<script setup>
import { useRouter } from 'vue-router'
import { auth } from '../../stores/auth'

defineProps({ items: { type: Array, required: true } })
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <aside class="sidebar">
    <nav>
      <RouterLink v-for="item in items" :key="item.to" :to="item.to" class="nav-item">
        <span class="nav-icon">{{ item.icon }}</span>{{ item.label }}
      </RouterLink>
      <a href="#" class="nav-item" @click.prevent="logout"><span class="nav-icon">⎋</span>Logout</a>
    </nav>
  </aside>
</template>
