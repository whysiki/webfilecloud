<template>
  <TopBar />
  <FileList />
</template>
<script>
import TopBar from "../components/TopBar.vue";
import FileList from "../components/FileList.vue";
export default {
  name: "FileListView",
  components: {
    TopBar,
    FileList,
  },
};
</script>
