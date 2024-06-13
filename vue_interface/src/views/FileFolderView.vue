<template>
  <TopBar />
  <FileFolderComponent />
  <BatchActionsComponent />
</template>

<script>
import FileFolderComponent from "../components/FileFolderComponent.vue";
import TopBar from "../components/TopBar.vue";
import BatchActionsComponent from "../components/BatchActionsComponent.vue";
// import SeachComponent from "../components/SeachComponent.vue";
export default {
  components: {
    FileFolderComponent,
    BatchActionsComponent,
    TopBar,
    // SeachComponent,
  },
};
</script>
