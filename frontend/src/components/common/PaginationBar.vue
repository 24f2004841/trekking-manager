<script setup>
defineProps({ page: { type: Number, required: true }, pages: { type: Number, required: true } })
defineEmits(['change'])
</script>

<template>
  <div v-if="pages > 1" class="pagination">
    <button :disabled="page === 1" @click="$emit('change', page - 1)">‹</button>
    <button v-for="p in pages" :key="p" :class="{ active: p === page }" @click="$emit('change', p)">
      {{ p }}
    </button>
    <button :disabled="page === pages" @click="$emit('change', page + 1)">›</button>
  </div>
</template>
