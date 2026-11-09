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
        rows.value = await api.getStaff(q.value);
    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}
onMounted(load);
watch(q, load);

async function toggle(s) {
    try {
        await api.setStaffBlacklist(s.id, !s.blacklisted);
    } catch (e) {
        error.value = e.message;
        return;
    }
    load();
}
</script>

<template>
    <div class="page-header">
        <h1 class="page-title">Trekking Staff List</h1>
        <RouterLink :to="{ name: 'admin-staff-new' }" class="btn-primary"
            >+ Create Staff</RouterLink
        >
    </div>
    <SearchBar v-model="q" placeholder="Search trekking staff..." />
    <p v-if="error" class="error">{{ error }}</p>
    <PersonTable :rows="rows" :loading="loading" @toggle-blacklist="toggle" />
    <InfoNote>Blacklisted staff cannot login or access the system.</InfoNote>
</template>
