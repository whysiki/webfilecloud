<template>
  <div class="file-search">
    <input
      type="text"
      v-model="searchQuery"
      class="search-input"
      placeholder="Search files... enter a file name"
    />
    <div v-if="searchResults.length > 0" class="search-results">
      <div v-for="file in searchResults" :key="file.id">
        <FileItemComponent :file="file" />
      </div>
    </div>
    <div v-else class="no-results">No results found</div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import FileItemComponent from "./FileItemComponent.vue"; // 导入 FileItemComponent 组件

export default {
  components: {
    FileItemComponent,
  },
  props: {
    files: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    const searchQuery = ref(""); // 存储搜索查询
    const searchResults = computed(() => {
      const query = searchQuery.value.trim().toLowerCase();
      if (!query) return []; // 如果搜索查询为空，则返回空数组
      return props.files.filter((file) => {
        // 根据文件名进行搜索
        return file.filename.toLowerCase().includes(query);
      });
    });

    return {
      searchQuery,
      searchResults,
    };
  },
};
</script>

<style scoped>
@import "./css/SearchComponent.css";
</style>
