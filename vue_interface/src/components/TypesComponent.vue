<template>
  <div class="file-type">
    <h3 class="fileTypeTitle" @click="toggleVisibility(fileType)">
      {{ fileType }}
    </h3>
    <ul v-if="visibleFileTypes.includes(fileType)" class="fileType-file-items">
      <OrderComponent :files="filesByType(fileType)" />
    </ul>
  </div>
</template>

<script>
import OrderComponent from "./OrderComponent.vue";

export default {
  components: {
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
};
</script>
