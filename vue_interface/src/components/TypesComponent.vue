<template>
  <div class="file-type">
    <h3 class="fileTypeTitle" @click="toggleVisibility(fileType)">
      {{ fileType }}
    </h3>
    <ul v-if="visibleFileTypes.includes(fileType)" class="fileType-file-items">
      <FileItemComponent
        v-for="file in filesByType(fileType)"
        :key="file.id"
        :file="file"
      />
    </ul>
  </div>
</template>

<script>
import FileItemComponent from "./FileItemComponent.vue"; // 导入 FileItemComponent 组件

export default {
  components: {
    FileItemComponent,
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
};
</script>
