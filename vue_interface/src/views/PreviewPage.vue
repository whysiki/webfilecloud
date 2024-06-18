<template>
  <div>
    <CodeComponent :link="link" v-if="isText || isCode" />
    <VideoComponent :videoUrl="link" v-if="isVideo" />
    <ImageComponent :imageUrl="link" v-if="isImage" />
  </div>
</template>

<script>
// path: "/preview/:type/:filename/:link",
import VideoComponent from "../components/Preview/VideoComponent.vue";
import CodeComponent from "../components/Preview/CodeComponent.vue";
import ImageComponent from "../components/Preview/ImageComponent.vue";
export default {
  name: "PreviewPage",
  components: {
    VideoComponent,
    CodeComponent,
    ImageComponent,
  },
  data() {
    return {
      // 初始化数据
      type: "",
      filename: "",
      link: "",
    };
  },
  created() {
    // 在组件创建时获取路由参数
    this.type = this.$route.params.type;
    this.filename = this.$route.params.filename;
    // 对 link 参数进行解码
    this.link = decodeURIComponent(this.$route.params.link);
  },
  computed: {
    isVideo() {
      const videoTypes = ["mp4", "webm", "ogg", "avi", "mov", "flv", "mkv"];
      return videoTypes.includes(this.filename.split(".").pop());
    },
    isText() {
      const textTypes = ["txt", "md", "html", "css", "js", "json", "xml"];
      return textTypes.includes(this.filename.split(".").pop());
    },
    isCode() {
      const codeTypes = [
        "py",
        "java",
        "js",
        "c",
        "cpp",
        "go",
        "rb",
        "swift",
        "php",
        "sql",
        "html",
        "css",
      ];
      return codeTypes.includes(this.filename.split(".").pop());
    },
    isImage() {
      const imageTypes = [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "bmp",
        "webp",
        "svg",
        "ico",
      ];
      return imageTypes.includes(this.filename.split(".").pop());
    },
  },
};
</script>

<style screen>
.scroll-to-top,
.scroll-to-bottom {
  display: none;
}
</style>
