// API layer. Every function maps to a Flask endpoint; response fields follow
// the database models (see backend/models.py).

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

// Registered in main.js: clears the session and sends the user to /login.
let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => (onUnauthorized = fn);

async function request(
  path,
  { method = "GET", body, skipAuthRedirect = false } = {},
) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && !skipAuthRedirect) onUnauthorized();
  if (!res.ok) throw new Error(data.message || "Request failed");
  return data;
}

const withQuery = (path, q) =>
  q ? `${path}?${new URLSearchParams({ q })}` : path;

export const api = {
  // ---- auth ----
  login({ email, password, role }) {
    return request("/auth/login", {
      method: "POST",
      body: { email, password, role },
      skipAuthRedirect: true,
    });
  },
  register({ email, password, name, username, contact }) {
    return request("/auth/register", {
      method: "POST",
      body: { email, password, name, username, contact },
      skipAuthRedirect: true,
    });
  },
  // Validates the stored token server-side and returns the current user.
  me() {
    return request("/auth/me", { skipAuthRedirect: true });
  },

  // ---- admin ----
  getDashboard() {
    return request("/admin/dashboard");
  },

  getTreks(q = "") {
    return request(withQuery("/admin/treks", q));
  },
  deleteTrek(id) {
    return request(`/admin/treks/${id}`, { method: "DELETE" });
  },

  getStaff(q = "") {
    return request(withQuery("/admin/staff", q));
  },
  createStaff({ name, email, contact, password, experience, status }) {
    return request("/admin/staff", {
      method: "POST",
      body: { name, email, contact, password, experience, status },
    });
  },
  setStaffBlacklist(id, blacklisted) {
    return request(`/admin/staff/${id}/blacklist`, {
      method: "PATCH",
      body: { blacklisted },
    });
  },

  getUsers(q = "") {
    return request(withQuery("/admin/users", q));
  },
  setUserBlacklist(id, blacklisted) {
    return request(`/admin/users/${id}/blacklist`, {
      method: "PATCH",
      body: { blacklisted },
    });
  },

  getBookings() {
    return request("/admin/bookings");
  },
};
