

- 每个类型的排序优化
- 文件树视图优化
- 预览优化
- 视频在线播放
- 修改用户名
- 查看服务器状态，内存，CPU占用

## 视频在线播放
npm install vue-video-player --save
import { VideoPlayer } from 'vue3-video-player'
import 'vue3-video-player/dist/vue3-video-player.css'

export default {
  components: {
    VideoPlayer
  },
  // ...
}
<video-player class="vjs-custom-skin" :options="playerOptions"></video-player>
data() {
  return {
    playerOptions: {
      autoplay: true,
      muted: true,
      language: 'en',
      playbackRates: [0.7, 1.0, 1.5, 2.0],
      sources: [
        {
          type: "video/mp4",
          src: "https://example.com/my-video.mp4"
        }
      ],
      poster: "https://example.com/my-video-poster.jpg",
      notSupportedMessage: 'This video is not supported in your browser',
    },
    // ...
  }
}

## pdf在线预览
npm install vue-pdf
import { pdfjs } from 'vue-pdf'

export default {
  components: {
    pdf: pdfjs.PdfViewer
  },
  // ...
}
<pdf src="https://example.com/my-document.pdf"></pdf>

## 代码
npm install highlight.js
import hljs from 'highlight.js'
import 'highlight.js/styles/default.css'

export default {
  mounted() {
    let blocks = this.$el.querySelectorAll('pre code');
    blocks.forEach((block) => {
      hljs.highlightBlock(block);
    });
  },
  // ...
}
<pre><code class="javascript">{{ yourCode }}</code></pre>
