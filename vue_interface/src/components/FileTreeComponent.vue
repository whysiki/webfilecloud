<template>
  <div class="file-tree">
    <div v-for="(value, key) in fileTree" :key="key" class="file-tree-item">
      <div v-if="!Array.isArray(value)">
        <!-- <div @click="toggleFolder(key)" class="folder-title">{{ key }}</div> -->
        <div @click="toggleFolder(key)" class="folder-title">
          <i :class="folderStates[key] ? 'fas fa-folder-open' : 'fas fa-folder'"></i>
          {{ key }}
        </div>
        <div v-if="folderStates[key]" class="folder-content">
          <FileTreeComponent :fileTreeSub="value" :parentPath="[...parentPath, key]" />
        </div>
      </div>
      <div v-else class="file-tree-items" :style="listStyle">
        <div v-for="file in value" :key="file.id">
          <FileItemComponent :file="file" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import FileItemComponent from "./FileItemComponent.vue";
import store from "../store";
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
      // currentNodes: [], // for tracking the current nodes
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
    listStyle() {
      if (store.state.viewMode === "card") {
        return {
          display: "flex",
          "flex-wrap": "wrap",
        };
      } else {
        return {};
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

      let currentNodes = fullPath;
      if (this.folderStates[folderName]) {
        currentNodes = [...this.parentPath, folderName];
      } else {
        currentNodes = fullPath.length > 1 ? fullPath.slice(0, fullPath.length - 1) : [];
      }

      this.emitter.emit("update-current-nodes", JSON.stringify(currentNodes.flat()));

      // console.log(currentNodes.flat().join("/"));
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
