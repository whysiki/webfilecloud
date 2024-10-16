<template>
  <div class="video-container">
    <!-- <video ref="videoElement" class="video-player" controls autoplay></video> -->
    <video ref="videoElement" class="video-player" controls></video>
  </div>
</template>

<script>
import Hls from "hls.js";

export default {
  name: "HlsPlayer",
  props: {
    src: {
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
              // console.log("newUrl", newUrl);
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
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100vh;
  background-color: #000;
}

.video-player {
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 100%;
}

@media (max-width: 768px) {
  .video-container {
    height: 50vh;
  }
}

@media (max-width: 480px) {
  .video-container {
    height: 30vh;
  }
}
</style>
