<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import InfoNote from "../components/common/InfoNote.vue";
import { api } from "../services/api";
import { auth, homeRouteFor } from "../stores/auth";

const router = useRouter();
const roles = [
    { value: "admin", label: "Admin", icon: "🧑‍💼" },
    { value: "staff", label: "Trekking Staff", icon: "🧭" },
    { value: "trekker", label: "User (Trekker)", icon: "🥾" },
];
const role = ref("admin");
const email = ref("");
const password = ref("");
const remember = ref(false);
const error = ref("");
const loading = ref(false);

async function submit() {
    error.value = "";
    loading.value = true;
    try {
        const { token, user } = await api.login({
            email: email.value,
            password: password.value,
            role: role.value,
        });
        const home = homeRouteFor(user.role);
        if (home.name === "login") {
            error.value = "This portal is not available yet.";
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
                <div class="roles-title">ROLES</div>
                <button
                    v-for="r in roles"
                    :key="r.value"
                    type="button"
                    class="role-btn"
                    :class="{ selected: role === r.value }"
                    @click="role = r.value"
                >
                    <span>{{ r.icon }}</span
                    >{{ r.label }}
                </button>
            </div>
        </div>

        <form class="login-card" @submit.prevent="submit">
            <h2>Welcome Back!</h2>
            <p class="muted">Login to your account</p>
            <input
                v-model="email"
                type="email"
                placeholder="Email address"
                required
            />
            <input
                v-model="password"
                type="password"
                placeholder="Password"
                required
            />
            <label class="checkbox"
                ><input v-model="remember" type="checkbox" /> Remember me</label
            >
            <p v-if="error" class="error">{{ error }}</p>
            <button class="btn-primary block" :disabled="loading">
                {{ loading ? "Logging in..." : "Login" }}
            </button>
            <p class="center muted">Don't have an account?</p>
            <p class="center">
                <router-link :to="{ name: 'register' }"
                    >Register as User (Trekker)</router-link
                >
            </p>
        </form>

        <InfoNote class="login-note">
            <strong>Note:</strong> Only Users (Trekkers) can register
            themselves.<br />
            Trekking Staff are created by Admin.
        </InfoNote>
    </div>
</template>
