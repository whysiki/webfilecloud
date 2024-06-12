<template>
  <div class="file-folder-view">
    <!-- 导航条 -->
    <nav class="navigation-bar">
      <div class="navigation-bar__path">
        <div @click="goBack" class="folder-title goback">Return</div>
        <div @click="navigateTo([])" class="folder-title">/</div>
        <div
          v-for="(path, index) in currentPath"
          :key="index"
          @click="navigateTo(currentPath.slice(0, index + 1))"
          class="folder-title"
        >
          > {{ path }}
        </div>
      </div>
    </nav>
    <!-- 子文件夹列表 -->
    <div v-if="subDirectories.length" class="file-folders">
      <div
        v-for="(directory, index) in subDirectories"
        :key="index"
        @click="navigateTo(directory)"
        class="file-folder-title"
      >
        <i class="fas fa-folder"></i>
        {{ directory[directory.length - 1] }}
        <!-- 显示最后一个 -->
      </div>
    </div>

    <!-- 文件列表 -->
    <div v-if="files.length > 0 && showOrderComponent" class="file-tree-items">
      <OrderComponent :files="files" />
    </div>
  </div>
</template>

<script>
import store from "../store";
import axios from "../axios";
import OrderComponent from "./OrderComponent";
import { ref } from "vue";

export default {
  components: {
    OrderComponent,
  },
  data() {
    return {
      subDirectories: [], // 当前路径下的子文件夹
      currentPath: [], // 当前路径
      showOrderComponent: true,
    };
  },
  setup() {
    const treePathList = ref(store.state.treePathList);
    let files = ref([]);
    return { treePathList, files };
  },
  created() {
    if (this.currentPath.length === 0) {
      this.navigateTo([]);
    }
  },
  mounted() {
    this.emitter.on("file-uploaded", this.navigateTo(this.currentPath));
    this.emitter.on("one-file-deleted", this.navigateTo(this.currentPath));
    this.emitter.on("one-file-moved", this.navigateTo(this.currentPath));
    this.emitter.on("all-files-deleted", this.navigateTo(this.currentPath));
    this.emitter.on("batch-files-moved", this.navigateTo(this.currentPath));
    this.emitter.on("batch-files-deleted", this.navigateTo(this.currentPath));
    this.emitter.on("one-file-updated", this.navigateTo(this.currentPath));
  },
  beforeUnmount() {
    this.emitter.off("file-uploaded", this.navigateTo(this.currentPath));
    this.emitter.off("one-file-deleted", this.navigateTo(this.currentPath));
    this.emitter.off("one-file-moved", this.navigateTo(this.currentPath));
    this.emitter.off("all-files-deleted", this.navigateTo(this.currentPath));
    this.emitter.off("batch-files-moved", this.navigateTo(this.currentPath));
    this.emitter.off("batch-files-deleted", this.navigateTo(this.currentPath));
    this.emitter.off("one-file-updated", this.navigateTo(this.currentPath));
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    // 导航到指定路径
    async navigateTo(path) {
      this.showOrderComponent = false;
      const fileNodes = JSON.stringify(path);
      const token = localStorage.getItem("token") || store.state.token;
      try {
        const response = await axios.get(
          `/files/nodefiles?file_nodes=${fileNodes}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        this.files = response.data.files;
        const subDirectories = this.treePathList.filter(
          (treePath) =>
            treePath.length === path.length + 1 &&
            JSON.stringify(treePath.slice(0, path.length)) ===
              JSON.stringify(path)
        );

        const subDirectoriesNoRepeat = Array.from(
          new Set(subDirectories.map(JSON.stringify))
        ).map(JSON.parse);
        this.subDirectories = subDirectoriesNoRepeat;
        this.currentPath = path.slice();
        this.showOrderComponent = true;
        // console.log("currentPath", this.currentPath);
        this.emitter.emit(
          "update-current-nodes",
          JSON.stringify(this.currentPath)
        );
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(
            `Error: ${error.response.data.detail}`
          );
        } else if (error.request) {
          await this.$refs.alertPopup.showAlert(
            "Error: No response from server"
          );
        } else {
          await this.$refs.alertPopup.showAlert("Error", error.message);
        }
      }
    },
  },
};
</script>
<style scoped>
@import "./css/FileFolderComponent.css";
</style>
