import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import { auth } from "./stores/auth";
import { setUnauthorizedHandler } from "./services/api";

// Any 401 from a protected API (expired / revoked / blacklisted) ends the session.
setUnauthorizedHandler(() => {
  auth.logout();
  if (router.currentRoute.value.name !== "login")
    router.push({ name: "login" });
});

createApp(App).use(router).mount("#app");
