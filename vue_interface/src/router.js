import { createRouter, createWebHashHistory } from "vue-router";

import Home from "./views/HomeView.vue";
import FileList from "./views/FileListView.vue";

const routes = [
  { path: "/", component: Home },
  {
    path: "/filelist",
    component: FileList,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
