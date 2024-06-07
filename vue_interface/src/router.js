import { createRouter, createWebHistory } from "vue-router";

import Home from "./views/HomeView.vue";
import FileList from "./views/FileListView.vue";

const routes = [
  { path: "/", component: Home },
  {
    path: "/filelist",
    components: {
      filelist: FileList,
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
