<template>
  <div class="video-container">
    <video ref="videoPlayer" class="video-player" controls></video>
  </div>
</template>

<script>
import shaka from "shaka-player";

export default {
  props: {
    videoUrl: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.initPlayer();
  },
  beforeUnmount() {
    if (this.player) {
      this.player.destroy();
    }
  },
  methods: {
    initPlayer() {
      // 初始化 Shaka Player
      shaka.polyfill.installAll();
      if (shaka.Player.isBrowserSupported()) {
        this.player = new shaka.Player(this.$refs.videoPlayer);

        // 错误监听
        this.player.addEventListener("error", this.onErrorEvent);

        // 尝试加载视频
        this.player.load(this.videoUrl).catch(this.onError);
      } else {
        console.error("Browser not supported!");
      }
    },
    onErrorEvent(event) {
      // 错误处理
      this.onError(event.detail);
    },
    onError(error) {
      console.error("Error code", error.code, "object", error);
    },
  },
};
</script>

<style scoped>
.video-container {
  width: 100%;
  align-items: center;
  /* display: flex; */
}
.video-player {
  width: 100%;
  height: auto;
}
</style>
