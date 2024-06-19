<template>
  <div
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
    class="swipe-back-container"
  >
    <CodeComponent :link="link" v-if="isCode || isText" />
    <!-- <VideoComponent :videoUrl="link" v-if="false" /> -->
    <HlsComponent
      :src="hlsLink"
      :fileId="id"
      :domainNamePrefix="domainNamePrefix"
      v-if="isVideo"
    />
    <ImageComponent :imageUrl="link" v-if="isImage" />
    <div
      v-if="!isCode && !isVideo && !isImage && !isText"
      class="default-preview"
    >
      <p class="text-center">No preview available</p>
      <a
        :href="link"
        download
        class="preview-button"
        id="preview-button-single-file"
        title="Click to preview file image or video or text"
        @click.stop
      >
        <i class="fas fa-download"></i>
      </a>
    </div>
  </div>
</template>

<script>
// path: "/preview/:type/:filename/:link",
// import VideoComponent from "../components/Preview/VideoComponent.vue";
import CodeComponent from "../components/Preview/CodeComponent.vue";
import ImageComponent from "../components/Preview/ImageComponent.vue";
import HlsComponent from "../components/Preview/HlsComponent.vue";
export default {
  name: "PreviewPage",
  components: {
    // VideoComponent,
    CodeComponent,
    ImageComponent,
    HlsComponent,
  },
  data() {
    return {
      // 初始化数据
      type: "",
      filename: "",
      link: "",
      id: "",
    };
  },
  created() {
    // 在组件创建时获取路由参数
    this.id = this.$route.params.id;
    this.type = this.$route.params.type;
    this.filename = this.$route.params.filename;
    // 对 link 参数进行解码
    this.link = decodeURIComponent(this.$route.params.link);
  },
  computed: {
    domainNamePrefix() {
      return this.link.match(/^https?:\/\/[^/]+/)[0];
    },
    hlsLink() {
      const domainNamePrefix = this.link.match(/^https?:\/\/[^/]+/)[0];

      // console.log("domainNamePrefix", domainNamePrefix);
      // console.log("this.id", this.id);
      // console.log("this.filename", this.filename);
      // console.log("this.link", this.link);
      return `${domainNamePrefix}/file/video/${this.id}/index.m3u8`;
    },
    isVideo() {
      const videoTypes = ["mp4", "webm", "ogg", "avi", "mov", "flv", "mkv"];
      return videoTypes.includes(this.filename.split(".").pop());
    },
    isText() {
      const textTypes = ["txt", "log", "conf", "cfg", "ini"];
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
        "scss",
        "json",
        "xml",
        "yaml",
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
  methods: {
    handleTouchStart(event) {
      // 记录触摸开始的位置
      this.touchStartX = event.touches[0].clientX;
      this.touchStartY = event.touches[0].clientY;
    },
    handleTouchEnd(event) {
      const touchEndX = event.changedTouches[0].clientX;
      const touchEndY = event.changedTouches[0].clientY;

      // 计算滑动距离
      const diffX = touchEndX - this.touchStartX;
      const diffY = touchEndY - this.touchStartY;

      // 判断是否为从左向右的滑动，并且滑动距离大于一定值，
      if (diffX > 150 && Math.abs(diffY) < 150) {
        // 执行返回操作
        this.$router.go(-1);
      }
    },
  },
};
</script>

<style scoped>
.swipe-back-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.default-preview {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.default-preview p {
  font-size: 24px;
  margin-top: 10vh;
  color: #e74c3c;
  font-weight: bold;
}

.preview-button {
  font-size: 35px;
  padding: 40px 40px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  margin-top: 10vh;
}
</style>
