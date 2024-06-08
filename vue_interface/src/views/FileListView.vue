<template>
  <TopBar />
  <FileList v-if="true" />
</template>

<script>
import TopBar from "../components/TopBar.vue";
import FileList from "../components/FileList.vue";
// import SearchComponent from "../components/SearchComponent.vue";
export default {
  name: "FileListView",
  components: {
    TopBar,
    FileList,
    // SearchComponent,
  },
};
</script>

<style screen></style>
