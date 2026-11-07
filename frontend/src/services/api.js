// API layer. The backend admin endpoints do not exist yet, so every function
// below resolves mock data. Replace the bodies with `request(...)` calls
// once the Flask routes are ready; views/components won't need to change.

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
const delay = (v) => new Promise((r) => setTimeout(() => r(v), 150));

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

// ---- mock data ----
let treks = [
  {
    id: 1,
    name: "Everest Base Camp",
    location: "Nepal",
    difficulty: "Hard",
    slots: 10,
    status: "Open",
  },
  {
    id: 2,
    name: "Roopkund Trek",
    location: "Uttarakhand",
    difficulty: "Moderate",
    slots: 15,
    status: "Open",
  },
  {
    id: 3,
    name: "Kedarkantha Trek",
    location: "Uttarakhand",
    difficulty: "Easy",
    slots: 20,
    status: "Closed",
  },
  {
    id: 4,
    name: "Hampta Pass",
    location: "Himachal",
    difficulty: "Moderate",
    slots: 12,
    status: "Open",
  },
];
let staff = [
  {
    id: "TS001",
    name: "Vikas Singh",
    email: "vikas@gmail.com",
    contact: "9876543210",
    blacklisted: false,
  },
  {
    id: "TS002",
    name: "Neha Joshi",
    email: "neha@gmail.com",
    contact: "9123456780",
    blacklisted: true,
  },
  {
    id: "TS003",
    name: "Arjun Mehta",
    email: "arjun@gmail.com",
    contact: "9986776655",
    blacklisted: false,
  },
  {
    id: "TS004",
    name: "Pooja Rawat",
    email: "pooja@gmail.com",
    contact: "9012345678",
    blacklisted: false,
  },
  {
    id: "TS005",
    name: "Rahim Khan",
    email: "rahim@gmail.com",
    contact: "9871122334",
    blacklisted: true,
  },
];
let users = [
  {
    id: "U001",
    name: "Amit Sharma",
    email: "amit@gmail.com",
    contact: "9876543210",
    blacklisted: false,
  },
  {
    id: "U002",
    name: "Priya Patel",
    email: "priya@gmail.com",
    contact: "9123456780",
    blacklisted: false,
  },
  {
    id: "U003",
    name: "Rahul Verma",
    email: "rahul@gmail.com",
    contact: "9986776655",
    blacklisted: true,
  },
  {
    id: "U004",
    name: "Sneha Iyer",
    email: "sneha@gmail.com",
    contact: "9123898765",
    blacklisted: false,
  },
  {
    id: "U005",
    name: "Karan Tiwari",
    email: "karan@gmail.com",
    contact: "9871234567",
    blacklisted: false,
  },
];
const bookings = [
  {
    id: "B001",
    user: "Amit Sharma",
    trek: "Everest Base Camp",
    date: "12 May 2026",
    status: "Booked",
  },
  {
    id: "B002",
    user: "Priya Patel",
    trek: "Roopkund Trek",
    date: "11 May 2026",
    status: "Booked",
  },
  {
    id: "B003",
    user: "Rahul Verma",
    trek: "Kedarkantha Trek",
    date: "10 May 2026",
    status: "Cancelled",
  },
];

const matches = (obj, q) =>
  !q || Object.values(obj).join(" ").toLowerCase().includes(q.toLowerCase());

export const api = {
  // Real endpoints
  login({ email, password, role }) {
    return request("/auth/login", {
      method: "POST",
      body: { email, password, role },
      skipAuthRedirect: true,
    });
  },
  // Validates the stored token server-side and returns the current user.
  me() {
    return request("/auth/me", { skipAuthRedirect: true });
  },

  // ---- everything below is still mocked ----

  async getDashboard() {
    return delay({
      totals: { treks: 25, users: 120, staff: 18, bookings: 185 },
      recentBookings: bookings,
    });
  },

  async getTreks(q = "") {
    return delay(treks.filter((t) => matches(t, q)));
  },
  async deleteTrek(id) {
    treks = treks.filter((t) => t.id !== id);
    return delay(true);
  },

  async getStaff(q = "") {
    return delay(staff.filter((s) => matches(s, q)));
  },
  async createStaff(payload) {
    const id = "TS" + String(staff.length + 1).padStart(3, "0");
    staff = [
      ...staff,
      {
        id,
        name: payload.name,
        email: payload.email,
        contact: payload.contact,
        blacklisted: false,
      },
    ];
    return delay({ id });
  },
  async setStaffBlacklist(id, blacklisted) {
    staff = staff.map((s) => (s.id === id ? { ...s, blacklisted } : s));
    return delay(true);
  },

  async getUsers(q = "") {
    return delay(users.filter((u) => matches(u, q)));
  },
  async setUserBlacklist(id, blacklisted) {
    users = users.map((u) => (u.id === id ? { ...u, blacklisted } : u));
    return delay(true);
  },

  async getBookings() {
    return delay(bookings);
  },
};
