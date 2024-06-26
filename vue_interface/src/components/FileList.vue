<template>
  <!-- 搜索视图 -->
  <SearchComponent :files="files" v-if="showSearch" />
  <!-- 批量操作组件 -->
  <BatchActionsComponent />
  <div class="file-list" v-if="!showSearch">
    <!-- 文件信息 -->
    <div class="user-info">
      <h2>
        <router-link to="/user">
          <!-- 用户头像 -->
          <!-- <i class="fas fa-user"></i> -->
          <img :src="userAvatar" alt="" class="user-avatar-small" />
        </router-link>
        <span class="file-owner">{{ firstFileOwner }}</span>
        <router-link to="/filefolder">
          <i class="fas fa-folder-open" id="user-info-fa-folder-open"></i>
        </router-link>
        <span class="file-count">{{ fileAllCount }}</span>
      </h2>
    </div>
    <!-- 按钮组 -->
    <!-- 按钮组 -->
    <div class="file-list-button-container">
      <button class="file-list-button collapseAll" @click="collapseAll">
        CollapseAll
      </button>
      <button class="file-list-button expandAll" @click="expandAll">ExpandAll</button>
      <div class="file-list-dropdown">
        <button class="file-list-button showMode" @click="toggleDropdown">
          <i class="fas fa-bars"></i>ViewMode
        </button>
        <ul class="dropdown-menu" v-if="dropdownOpen">
          <li @click="changeViewMode('ShowByType')">Show By Type</li>
          <li @click="changeViewMode('ShowByTree')">Show By Tree</li>
          <li @click="changeViewMode('SortFiles')">Sort Files</li>
        </ul>
      </div>
    </div>
    <!-- 文件类型视图 -->
    <div class="fileTypeView" v-if="viewMode === 'ShowByType' && !showSearch">
      <TypesComponent
        v-for="fileType in fileTypes"
        :key="fileType"
        :fileType="fileType"
        :visibleFileTypes="visibleFileTypes"
        :files="files"
        @toggle-visibility="toggleVisibility"
      />
    </div>
    <!-- 文件树视图 -->
    <div class="fileTreeView" v-if="viewMode === 'ShowByTree' && !showSearch">
      <FileTreeComponent :files="files" />
    </div>
    <!-- 排序视图 -->
    <div class="order-file-list" v-if="viewMode === 'SortFiles' && !showSearch">
      <OrderComponent :files="files" />
    </div>
    <!-- 弹出式警告组件 -->
    <AlertComponent ref="alertPopup" />
  </div>
</template>

<script>
import axios from "../axios"; // 导入 axios 实例
import TypesComponent from "./TypesComponent.vue"; // 导入 TypesComponent 组件
import FileTreeComponent from "./FileTreeComponent.vue"; // 导入 FileTreeComponent 组件
import OrderComponent from "./OrderComponent.vue";
import SearchComponent from "./SearchComponent.vue";
import BatchActionsComponent from "./BatchActionsComponent.vue";
import store from "../store";
import eventBus from "../eventBus";
import { provide, ref, onMounted } from "vue"; // 导入 provide 和 ref
// import { ref, onMounted } from "vue"; // 导入 ref 和 onMounted
const fetchEvents = [
  "file-uploaded",
  "one-file-deleted",
  "one-file-moved",
  "all-files-deleted",
  "batch-files-moved",
  "batch-files-deleted",
  "one-file-updated",
];
const getPrefixPaths = (arr) => {
  let prefixPaths = [];
  for (let i = 1; i <= arr.length; i++) {
    prefixPaths.push(arr.slice(0, i));
  }
  return prefixPaths;
};

export default {
  components: {
    TypesComponent,
    FileTreeComponent,
    OrderComponent,
    SearchComponent,
    BatchActionsComponent,
  },
  setup() {
    let files = ref([]);
    provide("files", files);

    let alertPopup = ref(null);
    const fetchFiles = async () => {
      try {
        const response = await axios.get("/files/list", {});
        files.value = response.data.files;
        localStorage.setItem("currentFilesLength", files.value.length);
        store.commit("setFiles", response.data.files);
        let treePathList = [];
        let uniquePaths = new Set();
        response.data.files.forEach((file) => {
          if (file.file_nodes.length > 0) {
            let prefixPaths = getPrefixPaths(file.file_nodes);
            prefixPaths.forEach((path) => {
              uniquePaths.add(JSON.stringify(path));
            });
          }
        });
        uniquePaths.forEach((path) => {
          treePathList.push(JSON.parse(path));
        });
        // console.log(treePathList);
        store.commit("buildTreePathList", treePathList);
      } catch (error) {
        if (alertPopup.value) {
          if (error.response) {
            await alertPopup.value.showAlert(`Error: ${error.response.data.detail}`);
          } else if (error.request) {
            await alertPopup.value.showAlert("Error: No response from server");
          } else {
            await alertPopup.value.showAlert("Error", error.message);
          }
        } else {
          console.error(error);
        }
      }
    };
    onMounted(async () => {
      if (
        localStorage.getItem("currentFilesLength") > 0 &&
        localStorage.getItem("currentFilesLength") == store.state.files.length
      ) {
        files.value = [...store.state.files];
      } else {
        await fetchFiles();
      }
      // const asyncFetchFiles = async () => await fetchFiles();
      // fetchEvents.forEach((event) => eventBus.on(event, asyncFetchFiles));
    });

    return { files, fetchFiles, alertPopup };
  },
  data() {
    return {
      visibleFileTypes: [],
      showClassByType: false,
      viewMode: "ShowByType",
      showSearch: false,
      dropdownOpen: false,
      userAvatar: localStorage.getItem("userAvatar")
        ? localStorage.getItem("userAvatar")
        : null,
    };
  },
  computed: {
    firstFileOwner() {
      const cachedUsername = localStorage.getItem("username");
      return this.files.length > 0 ? this.files[0].file_owner_name : cachedUsername;
    },
    fileAllCount() {
      return this.files.length;
    },
    fileTypes() {
      return [...new Set(this.files.map((file) => file.file_type))];
    },
  },
  mounted() {
    this.handleToggleSearch = (showSearch) => {
      this.showSearch = showSearch;
    };
    fetchEvents.forEach((event) => eventBus.on(event, this.fetchFiles));
    eventBus.on("toggle-search", this.handleToggleSearch);
  },
  beforeUnmount() {
    fetchEvents.forEach((event) => eventBus.off(event, this.fetchFiles));
    eventBus.off("toggle-search", this.handleToggleSearch);
  },
  async created() {
    await this.fetchAvatar();
  },
  methods: {
    checkImage(url) {
      return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(true);
        img.onerror = () => resolve(false);
        img.src = url;
      });
    },
    collapseAll() {
      this.visibleFileTypes = [];
      eventBus.emit("collapse-all");
    },
    expandAll() {
      this.visibleFileTypes = [...this.fileTypes];
      eventBus.emit("expand-all");
    },
    toggleVisibility(fileType) {
      const index = this.visibleFileTypes.indexOf(fileType);
      if (index >= 0) {
        this.visibleFileTypes.splice(index, 1);
      } else {
        this.visibleFileTypes.push(fileType);
      }
    },
    classByType() {
      switch (this.viewMode) {
        case "ShowByType":
          this.viewMode = "ShowByTree";
          break;
        case "ShowByTree":
          this.viewMode = "SortFiles";
          break;
        case "SortFiles":
          this.viewMode = "ShowByType";
          break;
      }
    },
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    changeViewMode(mode) {
      this.viewMode = mode;
      this.dropdownOpen = false;
    },
    async fetchAvatar() {
      try {
        const response = await axios.get("/users/profileimage", {
          headers: {
            "Content-Type": "application/octet-stream",
          },
          responseType: "blob",
        });
        this.userAvatar = URL.createObjectURL(new Blob([response.data]));
        localStorage.setItem("userAvatar", this.userAvatar);
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(`Error: ${error.response.data.detail}`);
        } else if (error.request) {
          await this.$refs.alertPopup.showAlert("Error: No response from server");
        } else {
          await this.$refs.alertPopup.showAlert("Error", error.message);
        }
      }
    },
  },
};
</script>

<style scoped>
@import "./css/FileList.css";
</style>
