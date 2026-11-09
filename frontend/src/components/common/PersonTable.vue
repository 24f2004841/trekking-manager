<script setup>
// Shared by Manage Staff and Manage Users (identical columns in the wireframe).
import StatusBadge from './StatusBadge.vue'

defineProps({ rows: { type: Array, required: true }, loading: Boolean })
defineEmits(['toggle-blacklist'])
</script>

<template>
  <table class="table">
    <thead>
      <tr><th>ID</th><th>Name</th><th>Email</th><th>Contact</th><th>Status</th><th>Action</th></tr>
    </thead>
    <tbody>
      <tr v-if="loading"><td colspan="6" class="muted center">Loading...</td></tr>
      <tr v-else-if="!rows.length"><td colspan="6" class="muted center">No records found</td></tr>
      <tr v-for="r in rows" :key="r.id">
        <td>{{ r.id }}</td>
        <td>{{ r.name }}</td>
        <td>{{ r.email }}</td>
        <td>{{ r.contact }}</td>
        <td><StatusBadge :status="r.blacklisted ? 'Blacklisted' : 'Active'" /></td>
        <td>
          <button
            class="btn-outline"
            :class="r.blacklisted ? 'btn-outline-green' : 'btn-outline-red'"
            @click="$emit('toggle-blacklist', r)"
          >
            {{ r.blacklisted ? 'Whitelist' : 'Blacklist' }}
          </button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
