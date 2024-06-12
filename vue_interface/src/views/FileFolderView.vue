<template>
  <TopBar />
  <FileFolderComponent />
  <!-- 批量操作组件 -->
  <BatchActionsComponent />
</template>

<script>
import FileFolderComponent from "../components/FileFolderComponent.vue";
import TopBar from "../components/TopBar.vue";
import BatchActionsComponent from "../components/BatchActionsComponent.vue";
export default {
  components: {
    FileFolderComponent,
    BatchActionsComponent,
    TopBar,
  },
};
</script>
