<script setup>
import { computed } from 'vue'

const props = defineProps({ status: { type: String, required: true } })

const kind = computed(
  () =>
    ({
      Active: 'green',
      Whitelist: 'green',
      Open: 'green',
      Booked: 'green',
      Completed: 'green',
      Blacklisted: 'red',
      Cancelled: 'red',
      Closed: 'gray',
    })[props.status] || 'gray',
)
</script>

<template>
  <span class="badge" :class="`badge-${kind}`">{{ status }}</span>
</template>
