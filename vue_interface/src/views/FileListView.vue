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
  data() {
    return {
      showScrollButton: false,
    };
  },
  mounted() {
    window.addEventListener("scroll", this.checkScroll);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.checkScroll);
  },
  methods: {
    checkScroll() {
      this.showScrollButton = window.scrollY > 50;
    },
    scrollToTop() {
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
  },
};
</script>
