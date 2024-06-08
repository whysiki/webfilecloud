import { createApp } from "vue";

import App from "./App.vue";

import router from "./router";

import "@fortawesome/fontawesome-free/css/all.css";

import AlertComponent from "./components/AlertComponent.vue";

import PopInputComponent from "./components/PopInputComponent.vue";
import mitt from "mitt";
const emitter = mitt();

let app = createApp(App);
app.component("AlertComponent", AlertComponent);
app.component("PopInputComponent", PopInputComponent);
app.use(router);
// app.use(store);
app.config.globalProperties.emitter = emitter;
app.mount("#app");
