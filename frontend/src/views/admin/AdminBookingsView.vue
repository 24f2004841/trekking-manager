<script setup>
import { onMounted, ref } from "vue";
import StatusBadge from "../../components/common/StatusBadge.vue";
import { api } from "../../services/api";
import { formatDate } from "../../utils/format";

const rows = ref([]);
const error = ref("");
onMounted(async () => {
    try {
        rows.value = await api.getBookings();
    } catch (e) {
        error.value = e.message;
    }
});
</script>

<template>
    <h1 class="page-title">Bookings</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <table class="table">
        <thead>
            <tr>
                <th>Booking ID</th>
                <th>User (Trekker)</th>
                <th>Trek</th>
                <th>Slots</th>
                <th>Booking Date</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            <tr v-if="!rows.length">
                <td colspan="6" class="muted center">No bookings found</td>
            </tr>
            <tr v-for="b in rows" :key="b.id">
                <td>{{ b.id }}</td>
                <td>{{ b.user }}</td>
                <td>{{ b.trek }}</td>
                <td>{{ b.num_slots }}</td>
                <td>{{ formatDate(b.booking_date) }}</td>
                <td><StatusBadge :status="b.status" /></td>
            </tr>
        </tbody>
    </table>
</template>
