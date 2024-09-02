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
    <MarkDownComponent :link="link" v-if="isMarkdown" />
    <div
      v-if="!isCode && !isVideo && !isImage && !isText && !isMarkdown"
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
import MarkDownComponent from "../components/Preview/MarkDownComponent.vue";
export default {
  name: "PreviewPage",
  components: {
    // VideoComponent,
    CodeComponent,
    ImageComponent,
    HlsComponent,
    MarkDownComponent,
  },
  data() {
    return {
      type: "",
      filename: "",
      link: "",
      id: "",
    };
  },
  created() {
    this.id = this.$route.params.id;
    this.type = this.$route.params.type;
    this.link = decodeURIComponent(this.$route.params.link);
  },
  computed: {
    domainNamePrefix() {
      return this.link.match(/^https?:\/\/[^/]+/)[0];
    },
    hlsLink() {
      const domainNamePrefix = this.link.match(/^https?:\/\/[^/]+/)[0];
      return `${domainNamePrefix}/file/video/${this.id}/index.m3u8`;
    },
    isVideo() {
      const videoTypes = ["mp4", "webm", "ogg", "avi", "mov", "flv", "mkv"];
      return videoTypes.includes(this.type);
    },
    isText() {
      const textTypes = ["txt", "log", "conf", "cfg", "ini"];
      return textTypes.includes(this.type);
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
      return codeTypes.includes(this.type);
    },
    isImage() {
      const imageTypes = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"];
      return imageTypes.includes(this.type);
    },
    isMarkdown() {
      return this.type === "md";
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
  /* margin: 10vh auto; */
  width: 95%;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
  margin-top: 10vh;
}

.default-preview p {
  font-size: 24px;
  color: #e74c3c;
  font-weight: bold;
}

.preview-button {
  font-size: 35px;
  padding: 35px 35px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  margin-top: 10vh;
}

/* 加载动画容器 */
:deep(.loader-container) {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.5); /* 半透明背景色 */
  z-index: 9999; /* 确保在最上层 */
}

/* 加载动画样式 */
:deep(.loader) {
  border: 8px solid #f3f3f3; /* Light grey */
  border-top: 8px solid #1a7be3; /* Blue */
  border-right: 8px solid #32cd32; /* Lime green */
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 2s linear infinite;
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px); /* 从下方移动进来 */
  }
  to {
    opacity: 1;
    transform: translateY(0); /* 最终位置 */
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
