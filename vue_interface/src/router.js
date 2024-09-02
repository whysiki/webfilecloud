import { createRouter, createWebHashHistory } from "vue-router";

import Home from "./views/HomeView.vue";
import FileList from "./views/FileListView.vue";
import UserView from "./views/UserView.vue";
// import path from "path-browserify";
import FileFolderView from "./views/FileFolderView.vue";
import PreviewPage from "./views/PreviewPage.vue";
// import path from "path-browserify";
// import path from "path-browserify";

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
  {
    path: "/preview/:id/:type/:link",
    component: PreviewPage,
  },
  {
    path: "/test_multiple_upload",
    component: () => import("./views/TestMultipartUpload.vue"),
  },
  {
    path: "/test_multiple_download",
    component: () => import("./views/TestMultipartDownload.vue"),
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
