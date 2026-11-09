<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import InfoNote from "../../components/common/InfoNote.vue";
import { api } from "../../services/api";

const router = useRouter();
const form = reactive({
    name: "",
    email: "",
    contact: "",
    password: "",
    confirm: "",
    experience: "",
    status: "Active",
});
const error = ref("");
const saving = ref(false);

async function submit() {
    error.value = "";
    if (form.password !== form.confirm) {
        error.value = "Passwords do not match";
        return;
    }
    saving.value = true;
    try {
        await api.createStaff({ ...form });
        router.push({ name: "admin-staff" });
    } catch (e) {
        error.value = e.message;
    } finally {
        saving.value = false;
    }
}
</script>

<template>
    <h1 class="page-title">Create New Trekking Staff</h1>
    <form class="card form-grid" @submit.prevent="submit">
        <input v-model="form.name" placeholder="Full Name" required />
        <input
            v-model="form.email"
            type="email"
            placeholder="Email Address"
            required
        />
        <input v-model="form.contact" placeholder="Contact Number" required />
        <input
            v-model="form.password"
            type="password"
            placeholder="Password"
            required
            minlength="8"
        />
        <input
            v-model="form.confirm"
            type="password"
            placeholder="Confirm Password"
            required
        />
        <input
            v-model.number="form.experience"
            class="span-2"
            type="number"
            min="0"
            step="1"
            placeholder="Experience (years)"
        />
        <label class="span-2 inline-field">
            Status
            <select v-model="form.status">
                <option>Active</option>
                <option>On Leave</option>
                <option>Inactive</option>
            </select>
        </label>
        <p v-if="error" class="error span-2">{{ error }}</p>
        <div class="span-2 form-actions">
            <button
                type="button"
                class="btn-outline-plain"
                @click="router.push({ name: 'admin-staff' })"
            >
                Cancel
            </button>
            <button class="btn-primary" :disabled="saving">Create Staff</button>
        </div>
    </form>
    <InfoNote
        >Share the login credentials with the staff member after creating the
        account.</InfoNote
    >
</template>
