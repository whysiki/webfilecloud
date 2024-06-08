<template>
  <!-- 搜索视图 -->
  <SearchComponent :files="files" v-if="showSearch" />
  <!-- 批量操作组件 -->
  <BatchActionsComponent />
  <div class="file-list" v-if="!showSearch">
    <!-- 文件信息 -->
    <div class="user-info">
      <h2>
        <i class="fas fa-user"></i>
        <span class="file-owner">{{ firstFileOwner }}</span>
        <i class="fas fa-folder-open" id="user-info-fa-folder-open"></i>
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
      <NavigationBar />
      <FileTreeComponent :files="files" />
    </div>

    <!-- 排序视图 -->
    <div class="order-file-list" v-if="viewMode === 'SortFiles' && !showSearch">
      <OrderComponent />
    </div>

    <!-- 弹出式警告组件 -->
    <AlertComponent ref="alertPopup" />
  </div>
</template>

<script>
import axios from "../axios"; // 导入 axios 实例
import TypesComponent from "./TypesComponent.vue"; // 导入 TypesComponent 组件
import FileTreeComponent from "./FileTreeComponent.vue"; // 导入 FileTreeComponent 组件
import NavigationBar from "./NavigationBar.vue";
import OrderComponent from "./OrderComponent.vue";
import SearchComponent from "./SearchComponent.vue";
import BatchActionsComponent from "./BatchActionsComponent.vue";
import store from "../store";
import { provide, ref } from "vue"; // 导入 provide 和 ref
export default {
  components: {
    TypesComponent,
    FileTreeComponent,
    NavigationBar,
    OrderComponent,
    SearchComponent,
    BatchActionsComponent,
  },
  setup() {
    const files = ref([]); // 使用 ref 创建一个响应式的数据对象
    provide("files", files); // 使用 provide 提供 files
    return { files };
  },
  data() {
    return {
      // files: [], // 初始化 files 数组
      visibleFileTypes: [], // 初始化 visibleFileTypes 数组
      showClassByType: false,
      viewMode: "ShowByType", // 初始化视图模式
      showSearch: false, // 初始化 showSearch 数据属性
      dropdownOpen: false,
      // viewMode: 'ShowByType'
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
  async created() {
    await this.fetchFiles();
  },
  mounted() {
    this.emitter.on("file-uploaded", this.fetchFiles);
    this.emitter.on("one-file-deleted", this.fetchFiles);
    this.emitter.on("one-file-moved", this.fetchFiles);
    this.emitter.on("all-files-deleted", this.fetchFiles);
    this.emitter.on("toggle-search", (showSearch) => {
      this.showSearch = showSearch;
    });
    this.emitter.on("batch-files-moved", this.fetchFiles);
    this.emitter.on("batch-files-deleted", this.fetchFiles);
  },
  beforeUnmount() {
    this.emitter.off("file-uploaded", this.fetchFiles);
    this.emitter.off("one-file-deleted", this.fetchFiles);
    this.emitter.off("one-file-moved", this.fetchFiles);
    this.emitter.off("all-files-deleted", this.fetchFiles);
    this.emitter.off("toggle-search", (showSearch) => {
      this.showSearch = showSearch;
    });
    this.emitter.off("batch-files-moved", this.fetchFiles);
    this.emitter.off("batch-files-deleted", this.fetchFiles);
  },
  methods: {
    collapseAll() {
      this.visibleFileTypes = [];
      this.emitter.emit("collapse-all");
    },
    expandAll() {
      this.visibleFileTypes = [...this.fileTypes];
      this.emitter.emit("expand-all");
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
    async fetchFiles() {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get("/files/list", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.files = response.data.files;
        localStorage.setItem("currentFilesLength", this.files.length);
        store.commit("setFiles", response.data.files);
      } catch (error) {
        await this.$refs.alertPopup.showAlert(`Error fetching files: ${error.message}`);
      }
    },

    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen;
    },
    changeViewMode(mode) {
      this.viewMode = mode;
      this.dropdownOpen = false;
    },
  },
};
</script>

<style scoped>
@import "./css/FileList.css";
</style>
