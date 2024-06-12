<template>
  <div class="file-type">
    <h3 class="fileTypeTitle" @click="toggleVisibility(fileType)">
      {{ fileType }}
    </h3>
    <ul
      v-if="visibleFileTypes.includes(fileType)"
      class="fileType-file-items"
      :style="listStyle"
    >
      <!-- <FileItemComponent
        v-for="file in filesByType(fileType)"
        :key="file.id"
        :file="file"
      /> -->
      <OrderComponent :files="filesByType(fileType)" />
    </ul>
  </div>
</template>

<script>
// import FileItemComponent from "./FileItemComponent.vue"; // 导入 FileItemComponent 组件
import store from "../store"; // 导入 store
import OrderComponent from "./OrderComponent.vue"; // 导入 OrderComponent 组件

export default {
  components: {
    // FileItemComponent,
    OrderComponent,
  },
  props: {
    fileType: {
      type: String,
      required: true,
    },
    visibleFileTypes: {
      type: Array,
      required: true,
    },
    files: {
      type: Array,
      required: true,
    },
  },
  methods: {
    toggleVisibility(fileType) {
      this.$emit("toggle-visibility", fileType);
    },
    filesByType(fileType) {
      return this.files.filter((file) => file.file_type === fileType);
    },
  },
  computed: {
    listStyle() {
      if (store.state.viewMode === "card") {
        return {
          // display: "grid",
          // "grid-template-columns": "repeat(auto-fill, minmax(auto, 3fr))", // let Grid adjust the size automatically
          // "grid-gap": "10px",
          display: "flex",
          flexWrap: "wrap",
          padding: 0,
          // display: "inline-block",
        };
      } else if (store.state.viewMode === "list") {
        return {
          display: "inline",
          "flex-wrap": "nowrap",
          padding: 0,
        };
      } else {
        return {
          display: "inline",
          "flex-wrap": "nowrap",
          padding: 0,
        };
      }
    },
  },
};
</script>
