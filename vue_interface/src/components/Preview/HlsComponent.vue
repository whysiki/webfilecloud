<template>
  <div class="video-container">
    <video ref="videoElement" class="video-player" controls autoplay></video>
  </div>
</template>

<script>
import Hls from "hls.js";

export default {
  name: "HlsPlayer",
  props: {
    src: {
      //("/file/video/{file_id}/index.m3u8")
      type: String,
      required: true,
    },
    fileId: {
      type: String,
      required: true,
    },
    domainNamePrefix: {
      type: String,
      required: true,
    },
  },
  mounted() {
    this.playVideo();
  },
  methods: {
    playVideo() {
      const video = this.$refs.videoElement;
      if (Hls.isSupported()) {
        const hls = new Hls({
          xhrSetup: (xhr, url) => {
            if (url.endsWith(".ts")) {
              const segmentName = url.split("/").pop();
              const newUrl = `${this.domainNamePrefix}/file/segments/${this.fileId}/${segmentName}`;
              console.log("newUrl", newUrl);
              xhr.open("GET", newUrl, true);
            }
          },
        });
        hls.loadSource(this.src);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
          video.play();
        });
      } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
        video.src = this.src;
        video.addEventListener("loadedmetadata", function () {
          video.play();
        });
      }
    },
  },
};
</script>

<style scoped>
.video-container {
  width: 100%;
  height: 100vh;
  align-items: center;
  justify-content: center;
  /* 垂直居中 */
  display: flex;
  /* display: flex; */
}
.video-player {
  /* margin-top: 50%; */
  width: 100%;
  height: auto;
}
</style>
