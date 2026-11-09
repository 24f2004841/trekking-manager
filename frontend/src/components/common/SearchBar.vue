<script setup>
defineProps({ modelValue: String, placeholder: { type: String, default: 'Search...' } })
defineEmits(['update:modelValue'])
</script>

<template>
  <div class="search-bar">
    <input
      type="text"
      :value="modelValue"
      :placeholder="placeholder"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <span>🔍</span>
  </div>
</template>
