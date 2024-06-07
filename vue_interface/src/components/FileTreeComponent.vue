<template>
  <div class="file-tree">
    <div v-for="(value, key) in fileTree" :key="key" class="file-tree-item">
      <div v-if="Array.isArray(value)" class="file-tree-items">
        <div v-for="file in value" :key="file.id">
          <FileItemComponent :file="file" />
        </div>
      </div>
      <div v-else>
        <!-- <div @click="toggleFolder(key)" class="folder-title">{{ key }}</div> -->
        <div @click="toggleFolder(key)" class="folder-title">
          <i :class="folderStates[key] ? 'fas fa-folder-open' : 'fas fa-folder'"></i>
          {{ key }}
        </div>
        <div v-if="folderStates[key]" class="folder-content">
          <FileTreeComponent :fileTreeSub="value" :parentPath="[...parentPath, key]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FileItemComponent from "./FileItemComponent.vue";

export default {
  components: {
    FileItemComponent,
  },
  props: {
    files: {
      type: Array,
      required: false,
    },
    fileTreeSub: {
      type: Object,
      required: false,
    },
    parentPath: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      folderStates: {},
      currentNodes: [], // for tracking the current nodes
    };
  },
  mounted() {
    this.emitter.on("expand-all", this.expandAll);
    this.emitter.on("collapse-all", this.collapseAll);
  },
  beforeUnmount() {
    this.emitter.off("expand-all", this.expandAll);
    this.emitter.off("collapse-all", this.collapseAll);
  },
  computed: {
    fileTree() {
      if (this.fileTreeSub) {
        return this.fileTreeSub;
      } else {
        if (!this.files) {
          return {};
        }
        return this.buildFileTree(this.files);
      }
    },
  },
  methods: {
    expandAll() {
      for (let key in this.folderStates) {
        this.folderStates[key] = true;
      }
    },
    collapseAll() {
      for (let key in this.folderStates) {
        this.folderStates[key] = false;
      }
    },
    toggleFolder(folderName) {
      this.folderStates[folderName] = !this.folderStates[folderName];
      // 获取完整的路径
      const fullPath = [...this.parentPath, folderName];

      // 如果文件夹被展开，将其添加到 currentNodes 中
      if (this.folderStates[folderName]) {
        this.currentNodes.push(fullPath);
      } else {
        // 如果文件夹被关闭，将其从 currentNodes 中移除
        const index = this.currentNodes.findIndex(
          (path) =>
            Array.isArray(path) && path.map(String).join("/") === fullPath.join("/")
        );
        if (index > -1) {
          this.currentNodes.splice(index, 1);
        }
        // 如果有父文件夹，将父文件夹的路径添加到 currentNodes 中
        if (this.parentPath.length > 0) {
          const parentPath = this.parentPath[this.parentPath.length - 1];
          if (!this.currentNodes.includes(parentPath)) {
            this.currentNodes.push(parentPath);
          }
        }
      }
      // 将 currentNodes 保存到 localStorage 中
      // localStorage.setItem("currentNodes", JSON.stringify(this.currentNodes.flat()));

      // console.log(localStorage.getItem("currentNodes"));
      this.emitter.emit("update-current-nodes", JSON.stringify(this.currentNodes.flat()));
    },
    buildFileTree(files) {
      const root = {};

      files.forEach((file) => {
        let currentNode = root;
        file.file_nodes.forEach((node, index) => {
          if (!currentNode[node]) {
            currentNode[node] = {};
          }
          currentNode = currentNode[node];
          if (index === file.file_nodes.length - 1) {
            if (!currentNode.files) {
              currentNode.files = [];
            }
            currentNode.files.push(file);
          }
        });
        if (file.file_nodes.length === 0) {
          if (!root.files) {
            root.files = [];
          }
          root.files.push(file);
        }
      });
      return root;
    },
  },
};
</script>

<style scoped>
@import "./css/FileTreeComponent.css";
</style>
