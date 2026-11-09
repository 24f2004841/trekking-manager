<script setup>
import { computed, onMounted, ref, watch } from "vue";
import SearchBar from "../../components/common/SearchBar.vue";
import StatusBadge from "../../components/common/StatusBadge.vue";
import PaginationBar from "../../components/common/PaginationBar.vue";
import { api } from "../../services/api";

const PAGE_SIZE = 4;
const treks = ref([]);
const q = ref("");
const page = ref(1);
const error = ref("");

async function load() {
    try {
        error.value = "";
        treks.value = await api.getTreks(q.value);
    } catch (e) {
        error.value = e.message;
    }
}
onMounted(load);
watch(q, () => {
    page.value = 1;
    load();
});

const pages = computed(() =>
    Math.max(1, Math.ceil(treks.value.length / PAGE_SIZE)),
);
const visible = computed(() =>
    treks.value.slice((page.value - 1) * PAGE_SIZE, page.value * PAGE_SIZE),
);

async function remove(t) {
    if (!confirm(`Delete "${t.name}"?`)) return;
    try {
        await api.deleteTrek(t.id);
    } catch (e) {
        error.value = e.message;
        return;
    }
    load();
}
</script>

<template>
    <div class="page-header">
        <h1 class="page-title">Treks</h1>
        <button class="btn-primary" @click="$emit('add')">
            + Add New Trek
        </button>
    </div>
    <SearchBar v-model="q" placeholder="Search treks..." />
    <p v-if="error" class="error">{{ error }}</p>

    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Trek Name</th>
                <th>Location</th>
                <th>Difficulty</th>
                <th>Available / Total Slots</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr v-if="!visible.length">
                <td colspan="7" class="muted center">No treks found</td>
            </tr>
            <tr v-for="t in visible" :key="t.id">
                <td>{{ t.id }}</td>
                <td>{{ t.name }}</td>
                <td>{{ t.location }}</td>
                <td>{{ t.difficulty }}</td>
                <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
                <td><StatusBadge :status="t.status" /></td>
                <td>
                    <button class="icon-btn" title="Edit">✎</button>
                    <button class="icon-btn" title="Delete" @click="remove(t)">
                        🗑
                    </button>
                </td>
            </tr>
        </tbody>
    </table>
    <PaginationBar :page="page" :pages="pages" @change="page = $event" />
</template>
