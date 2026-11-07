import { reactive } from "vue";
import { api } from "../services/api";

const TOKEN_KEY = "token";
const USER_KEY = "user";

const state = reactive({
  token: localStorage.getItem(TOKEN_KEY),
  user: JSON.parse(localStorage.getItem(USER_KEY) || "null"),
});

// Local expiry check only avoids a pointless request. The server stays the authority.
function isExpired(token) {
  try {
    const { exp } = JSON.parse(
      atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")),
    );
    return exp * 1000 <= Date.now();
  } catch {
    return true;
  }
}

let initPromise = null;

export const auth = {
  state,
  get isLoggedIn() {
    return !!state.token;
  },
  get role() {
    return state.user?.role || null;
  },
  setSession(token, user) {
    state.token = token;
    state.user = user;
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    initPromise = Promise.resolve(); // fresh login is already verified
  },
  logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    initPromise = Promise.resolve();
  },
  // Runs once per page load: validates the stored token with GET /auth/me and
  // refreshes the user (role, name) from the database.
  init() {
    if (!initPromise) {
      initPromise = (async () => {
        if (!state.token) return;
        if (isExpired(state.token)) return this.logout();
        try {
          const { user } = await api.me();
          state.user = user;
          localStorage.setItem(USER_KEY, JSON.stringify(user));
        } catch (e) {
          // Rejected token -> logout. Network errors keep the session so a
          // backend hiccup doesn't sign everyone out.
          if (e instanceof TypeError === false) this.logout();
        }
      })();
    }
    return initPromise;
  },
};

export const homeRouteFor = (role) =>
  ({ admin: { name: "admin-dashboard" } })[role] || { name: "login" };
