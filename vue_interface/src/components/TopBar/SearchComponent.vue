<!-- SearchComponent.vue -->
<template>
  <button
    class="top-bar-icon-button search"
    @click="toggleSearch"
    title="Search"
  >
    <i class="fas fa-search"></i>
  </button>
</template>

<script>
import { ref } from "vue";
import eventBus from "../../eventBus.js"; // 导入事件总线

export default {
  name: "SearchComponent",
  setup() {
    const showSearch = ref(false); // 创建一个响应式的布尔变量
    const toggleSearch = () => {
      eventBus.emit("toggle-search", !showSearch.value); // 触发事件总线事件
      showSearch.value = !showSearch.value; // 修改响应式变量的值
    };

    return {
      showSearch,
      toggleSearch,
    };
  },
};
</script>
