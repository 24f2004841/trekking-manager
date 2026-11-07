import { createRouter, createWebHistory } from "vue-router";
import { auth, homeRouteFor } from "../stores/auth";

import LoginView from "../views/LoginView.vue";

import AdminLayout from "../layouts/AdminLayout.vue";
import AdminDashboard from "../views/admin/AdminDashboardView.vue";
import AdminTreksView from "../views/admin/AdminTreksView.vue";
import AdminStaffListView from "../views/admin/AdminStaffListView.vue";
import AdminStaffCreateView from "../views/admin/AdminStaffCreateView.vue";
import AdminUsersView from "../views/admin/AdminUsersView.vue";
import AdminBookingsView from "../views/admin/AdminBookingsView.vue";

const routes = [
  { path: "/", redirect: "/login" },
  {
    path: "/login",
    name: "login",
    component: () => LoginView,
  },
  {
    path: "/admin",
    component: () => AdminLayout,
    meta: { requiresAuth: true, role: "admin" },
    children: [
      { path: "", redirect: { name: "admin-dashboard" } },
      {
        path: "dashboard",
        name: "admin-dashboard",
        component: () => AdminDashboard,
      },
      { path: "treks", name: "admin-treks", component: () => AdminTreksView },
      {
        path: "staff",
        name: "admin-staff",
        component: () => AdminStaffListView,
      },
      {
        path: "staff/new",
        name: "admin-staff-new",
        component: () => AdminStaffCreateView,
      },
      { path: "users", name: "admin-users", component: () => AdminUsersView },
      {
        path: "bookings",
        name: "admin-bookings",
        component: () => AdminBookingsView,
      },
      {
        path: "search",
        name: "admin-search",
        component: () => import("../views/admin/AdminPlaceholderView.vue"),
        props: { title: "Search" },
      },
      {
        path: "reports",
        name: "admin-reports",
        component: () => import("../views/admin/AdminPlaceholderView.vue"),
        props: { title: "Reports" },
      },
      {
        path: "settings",
        name: "admin-settings",
        component: () => import("../views/admin/AdminPlaceholderView.vue"),
        props: { title: "Settings" },
      },
    ],
  },
  { path: "/:pathMatch(.*)*", redirect: "/login" },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach(async (to) => {
  await auth.init(); // validates the stored token once per page load
  const needsAuth = to.matched.some((r) => r.meta.requiresAuth);
  const requiredRole = to.matched.find((r) => r.meta.role)?.meta.role;
  if (needsAuth && !auth.isLoggedIn) return { name: "login" };
  if (requiredRole && auth.role !== requiredRole) return { name: "login" };
  // Valid session on the login page: go straight to the role's home.
  if (to.name === "login" && auth.isLoggedIn) {
    const home = homeRouteFor(auth.role);
    if (home.name !== "login") return home;
  }
});

export default router;
