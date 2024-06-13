<template>
  <NavigationBar v-if="files && files.length > 0" />
  <div class="file-tree">
    <div v-for="(value, key) in fileTree" :key="key" class="file-tree-item">
      <div v-if="!Array.isArray(value)">
        <div @click="toggleFolder(key)" class="folder-title">
          <i
            :class="folderStates[key] ? 'fas fa-folder-open' : 'fas fa-folder'"
          ></i>
          {{ key }}
        </div>
        <div v-if="folderStates[key]" class="folder-content">
          <FileTreeComponent
            :fileTreeSub="value"
            :parentPath="[...parentPath, key]"
          />
        </div>
      </div>
      <div v-else class="file-tree-items">
        <OrderComponent :files="value" />
      </div>
    </div>
  </div>
</template>

<script>
import NavigationBar from "./NavigationBar.vue";
import OrderComponent from "./OrderComponent.vue";
import eventBus from "../eventBus";
// const events = ["expand-all", "collapse-all"];
export default {
  components: {
    OrderComponent,
    NavigationBar,
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
    };
  },
  mounted() {
    eventBus.on("expand-all", this.expandAll);
    eventBus.on("collapse-all", this.collapseAll);
  },
  beforeUnmount() {
    eventBus.off("expand-all", this.expandAll);
    eventBus.off("collapse-all", this.collapseAll);
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

      let currentNodes = fullPath;
      if (this.folderStates[folderName]) {
        currentNodes = [...this.parentPath, folderName];
      } else {
        currentNodes =
          fullPath.length > 1 ? fullPath.slice(0, fullPath.length - 1) : [];
      }

      eventBus.emit(
        "update-current-nodes",
        JSON.stringify(currentNodes.flat())
      );
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

      const sortedRoot = {};
      Object.keys(root)
        .sort((a, b) => {
          if (Array.isArray(root[a]) && !Array.isArray(root[b])) {
            return 1;
          }
          if (!Array.isArray(root[a]) && Array.isArray(root[b])) {
            return -1;
          }
          return 0;
        })
        .forEach((key) => {
          sortedRoot[key] = root[key];
        });

      return sortedRoot;
    },
  },
};
</script>

<style scoped>
@import "./css/FileTreeComponent.css";
</style>
