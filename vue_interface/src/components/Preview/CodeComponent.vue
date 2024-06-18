<template>
  <div class="code-container">
    <pre><code class="hljs" v-html="highlightedCode"></code></pre>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css"; // 默认加载一个主题

export default {
  components: {
    // NSelect,
  },
  props: {
    link: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const highlightedCode = ref("");

    const fetchAndHighlightCode = async () => {
      try {
        const response = await fetch(props.link);
        if (!response.ok) {
          throw new Error(`Error fetching code: ${response.statusText}`);
        }
        const code = await response.text();
        highlightedCode.value = hljs.highlightAuto(code).value;
      } catch (error) {
        console.error("Failed to fetch and highlight code:", error);
        highlightedCode.value = "Failed to load code.";
      }
    };

    onMounted(fetchAndHighlightCode);

    return {
      highlightedCode,
    };
  },
};
</script>

<style scoped>
/* 添加滚动条样式 */
.code-container {
  width: 100%;
  height: 100%;
  max-height: 100vh;
  overflow-y: auto; /* 在垂直方向上添加滚动条 */
}

/* 使代码自动换行 */
pre,
.hljs {
  white-space: pre-wrap; /* 保持格式但允许换行 */
  word-wrap: break-word; /* 在长单词或URL地址内部进行换行 */
}

/* 针对手机屏幕优化 */
@media (max-width: 600px) {
  .code-container {
    max-height: 100vh;
  }
  pre,
  .hljs {
    font-size: 14px; /* 减小字体大小以更好地适应小屏幕 */
  }
}
</style>
