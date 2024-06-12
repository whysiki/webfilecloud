import { createRouter, createWebHashHistory } from "vue-router";

import Home from "./views/HomeView.vue";
import FileList from "./views/FileListView.vue";
import UserView from "./views/UserView.vue";
// import path from "path-browserify";
import FileFolderView from "./views/FileFolderView.vue";

const routes = [
  { path: "/", component: Home },
  {
    path: "/filelist",
    component: FileList,
  },
  {
    path: "/user",
    component: UserView,
  },
  {
    path: "/filefolder",
    component: FileFolderView,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
