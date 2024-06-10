import { createRouter, createWebHashHistory } from "vue-router";

import Home from "./views/HomeView.vue";
import FileList from "./views/FileListView.vue";
import UserView from "./views/UserView.vue";

const routes = [
  { path: "/", component: Home },
  {
    path: "/filelist",
    component: FileList,
  },
  {
    path: "/user/:id",
    component: UserView,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
