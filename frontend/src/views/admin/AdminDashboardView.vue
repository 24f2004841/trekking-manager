<script setup>
import { onMounted, ref } from "vue";
import StatCard from "../../components/common/StatCard.vue";
import StatusBadge from "../../components/common/StatusBadge.vue";
import { api } from "../../services/api";
import { formatDate } from "../../utils/format";

const data = ref(null);
const error = ref("");
onMounted(async () => {
    try {
        data.value = await api.getDashboard();
    } catch (e) {
        error.value = e.message;
    }
});
</script>

<template>
    <h1 class="page-title">Dashboard</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <template v-if="data">
        <div class="stat-grid">
            <StatCard label="Total Treks" :value="data.totals.treks" icon="⛰" />
            <StatCard
                label="Total Users (Trekkers)"
                :value="data.totals.users"
                icon="👥"
            />
            <StatCard
                label="Total Trekking Staff"
                :value="data.totals.staff"
                icon="🧭"
            />
            <StatCard
                label="Total Bookings"
                :value="data.totals.bookings"
                icon="📅"
            />
        </div>

        <h3>Recent Bookings</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Booking ID</th>
                    <th>User (Trekker)</th>
                    <th>Trek</th>
                    <th>Booking Date</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-if="!data.recentBookings.length">
                    <td colspan="5" class="muted center">No bookings yet</td>
                </tr>
                <tr v-for="b in data.recentBookings" :key="b.id">
                    <td>{{ b.id }}</td>
                    <td>{{ b.user }}</td>
                    <td>{{ b.trek }}</td>
                    <td>{{ formatDate(b.booking_date) }}</td>
                    <td><StatusBadge :status="b.status" /></td>
                </tr>
            </tbody>
        </table>
        <p class="right">
            <RouterLink :to="{ name: 'admin-bookings' }"
                >View All Bookings →</RouterLink
            >
        </p>
    </template>
</template>
