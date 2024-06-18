<template>
  <SeachComponent :files="files" v-if="showSearch" />
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
import eventBus from "../eventBus";
import { ref } from "vue";
import SeachComponent from "./SearchComponent";
const eventNames = [
  "file-uploaded",
  "one-file-deleted",
  "one-file-moved",
  "all-files-deleted",
  "batch-files-moved",
  "batch-files-deleted",
  "one-file-updated",
];
export default {
  components: {
    OrderComponent,
    SeachComponent,
  },
  data() {
    return {
      subDirectories: [], // 当前路径下的子文件夹
      currentPath: [], // 当前路径
      showOrderComponent: true,
      showSearch: false,
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
    this.handleEvent = () => this.navigateTo(this.currentPath);
    eventNames.forEach((event) => eventBus.on(event, this.handleEvent));
    eventBus.on("toggle-search", (value) => {
      this.showSearch = value;
    });
  },
  beforeUnmount() {
    eventNames.forEach((event) => eventBus.off(event, this.handleEvent));
    eventBus.off("toggle-search", (value) => {
      this.showSearch = value;
    });
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    // 导航到指定路径
    async navigateTo(path) {
      this.showOrderComponent = false;
      const fileNodes = JSON.stringify(path);
      try {
        const response = await axios.get(
          `/files/nodefiles?file_nodes=${fileNodes}`,
          {}
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
        eventBus.emit("update-current-nodes", JSON.stringify(this.currentPath));
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
/* @import "./css/FileFolderComponent.css"; */
.file-folder-view {
  width: 95%;

  margin: 10px auto;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  align-items: center;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.5);
  /* margin: 20px 0; */
}
.navigation-bar {
  display: flex;
  flex-wrap: wrap;
}
.folder-title {
  font-weight: bold;
  background-color: #16723c;
  border-radius: 10px;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.folder-title:hover {
  /* background-color: #16723c; */
  background-color: #0056b3;
}
.folder-title.goback {
  background-color: #0056b3;
}

.file-tree-items {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  align-items: center;
}
.file-folder-title {
  margin-bottom: 10px;
  font-weight: bold;
  background-color: rgba(0, 86, 179, 0.5);
  border-radius: 10px;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.5);
  padding: 10px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.file-folder-title:hover {
  background-color: #16723c;
}
.file-folders > * {
  margin: 10px;
}
.folder-icon {
  width: 20px;
  height: 20px;
  margin-right: 5px;
}
.navigation-bar__path {
  display: flex;
  flex-wrap: wrap;
}
</style>
