<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import InfoNote from "../components/common/InfoNote.vue";
import { api } from "../services/api";
import { auth, homeRouteFor } from "../stores/auth";

const router = useRouter();
const form = reactive({
    name: "",
    email: "",
    contact: "",
    password: "",
    confirm: "",
});
const error = ref("");
const success = ref("");
const loading = ref(false);

async function submit() {
    error.value = "";
    success.value = "";
    if (form.password !== form.confirm) {
        error.value = "Passwords do not match";
        return;
    }
    loading.value = true;
    try {
        const { token, user } = await api.register({
            name: form.name,
            email: form.email,
            contact: form.contact,
            password: form.password,
        });
        const home = homeRouteFor(user.role);
        if (home.name === "login") {
            // No portal for trekkers yet: don't start a session, send them to login.
            success.value = "Account created successfully. You can now log in.";
            return;
        }
        auth.setSession(token, user);
        router.push(home);
    } catch (e) {
        error.value = e.message;
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <div class="login-page">
        <div class="login-hero">
            <h1>⛰ Trekking Management<br />Application</h1>
            <div class="roles">
                <div class="roles-title">REGISTERING AS</div>
                <div class="role-btn selected">
                    <span>🥾</span>User (Trekker)
                </div>
            </div>
        </div>

        <form class="login-card" @submit.prevent="submit">
            <h2>Create Account</h2>
            <p class="muted">Register as a User (Trekker)</p>
            <input
                v-model="form.name"
                placeholder="Full name"
                autocomplete="name"
                required
            />
            <input
                v-model="form.email"
                type="email"
                placeholder="Email address"
                autocomplete="email"
                required
            />
            <input
                v-model="form.contact"
                type="tel"
                placeholder="Contact number"
                autocomplete="tel"
            />
            <input
                v-model="form.password"
                type="password"
                placeholder="Password"
                autocomplete="new-password"
                minlength="6"
                required
            />
            <input
                v-model="form.confirm"
                type="password"
                placeholder="Confirm password"
                autocomplete="new-password"
                required
            />
            <p v-if="error" class="error">{{ error }}</p>
            <p v-if="success" class="success">{{ success }}</p>
            <button class="btn-primary block" :disabled="loading">
                {{ loading ? "Registering..." : "Register" }}
            </button>
            <p class="center muted">Already have an account?</p>
            <p class="center">
                <router-link :to="{ name: 'login' }">Back to Login</router-link>
            </p>
        </form>

        <InfoNote class="login-note">
            <strong>Note:</strong> Only Users (Trekkers) can register
            themselves.<br />
            Trekking Staff are created by Admin.
        </InfoNote>
    </div>
</template>
