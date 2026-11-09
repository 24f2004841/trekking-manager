<script setup>
import { onMounted, ref, watch } from "vue";
import SearchBar from "../../components/common/SearchBar.vue";
import PersonTable from "../../components/common/PersonTable.vue";
import InfoNote from "../../components/common/InfoNote.vue";
import { api } from "../../services/api";

const rows = ref([]);
const q = ref("");
const loading = ref(false);
const error = ref("");

async function load() {
    loading.value = true;
    try {
        error.value = "";
        rows.value = await api.getUsers(q.value);
    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}
onMounted(load);
watch(q, load);

async function toggle(u) {
    try {
        await api.setUserBlacklist(u.id, !u.blacklisted);
    } catch (e) {
        error.value = e.message;
        return;
    }
    load();
}
</script>

<template>
    <h1 class="page-title">Users (Trekkers)</h1>
    <SearchBar v-model="q" placeholder="Search users..." />
    <p v-if="error" class="error">{{ error }}</p>
    <PersonTable :rows="rows" :loading="loading" @toggle-blacklist="toggle" />
    <InfoNote>Blacklisted users cannot login or book treks.</InfoNote>
</template>
