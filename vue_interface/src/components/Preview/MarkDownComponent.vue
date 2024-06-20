<template>
  <div>
    <div v-if="isLoading" class="loader-container">
      <div class="loader"></div>
    </div>
    <div v-else class="markdown-component">
      <div class="sidebar">
        <nav v-if="tableOfContents.length">
          <ul>
            <li v-for="item in tableOfContents" :key="item.id">
              <a href="#" @click.prevent="scrollToAnchor(item.href)">{{
                item.title
              }}</a>
            </li>
          </ul>
        </nav>
      </div>
      <div v-html="compiledMarkdown" class="content"></div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import MarkdownIt from "markdown-it";
import MarkdownItAnchor from "markdown-it-anchor";
import MarkdownItTocDoneRight from "markdown-it-toc-done-right";

export default {
  name: "MarkdownReader",
  props: {
    link: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      md: new MarkdownIt()
        .use(MarkdownItAnchor, { permalink: false })
        .use(MarkdownItTocDoneRight, { listType: "ul" }),
      compiledMarkdown: "",
      tableOfContents: [],
      isLoading: true,
    };
  },
  watch: {
    link: "fetchAndRenderMarkdown",
  },
  created() {
    this.fetchAndRenderMarkdown();
  },
  methods: {
    async fetchAndRenderMarkdown() {
      this.isLoading = true;
      try {
        const response = await axios.get(this.link);
        const markdown = response.data;
        const rendered = this.md.render(markdown);
        this.compiledMarkdown = rendered;
        this.tableOfContents = this.extractToc(rendered);
      } catch (error) {
        console.error("Error fetching or rendering markdown:", error);
      } finally {
        this.isLoading = false;
      }
    },
    extractToc(renderedHtml) {
      const toc = [];
      const parser = new DOMParser();
      const doc = parser.parseFromString(renderedHtml, "text/html");
      doc.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach((heading) => {
        const id = heading.getAttribute("id");
        if (id) {
          toc.push({
            id: id,
            title: heading.textContent,
            href: `#${id}`,
          });
        }
      });
      return toc;
    },
    scrollToAnchor(href) {
      const anchor = href.substring(1); // Remove '#'
      const element = document.getElementById(anchor);
      if (element) {
        element.scrollIntoView({ behavior: "smooth" });
      }
    },
  },
};
</script>

<style>
.markdown-component {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.sidebar {
  margin-top: 20px;
  background-color: rgba(255, 255, 255, 0.7);
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  overflow-y: auto;
  z-index: 990;
}

.sidebar nav ul {
  list-style: none;
  padding: 10px;
}

.sidebar nav ul li {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  transition: background-color 0.3s ease;
  cursor: pointer;
  border-radius: 5px;
}

.sidebar nav ul li:hover {
  background-color: #f3f3f3;
}

.sidebar nav ul li a {
  color: #007bff;
  text-decoration: none;
}

.content {
  margin: 20px;
  padding: 20px 40px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.content h1,
.content h2,
.content h3,
.content h4,
.content h5,
.content h6 {
  margin-top: 20px;
  font-weight: bold;
  color: #3498db;
}

.content p {
  margin: 10px 0;
  line-height: 1.6;
  color: #555;
}

.content a {
  color: #3498db;
  text-decoration: none;
  border-bottom: 1px solid #3498db;
  transition:
    color 0.3s ease,
    border-bottom-color 0.3s ease;
}

.content a:hover {
  color: #16723c;
  border-bottom-color: #16723c;
}

.content code {
  font-family: Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace;
  background-color: rgba(0, 86, 179, 0.1);
  padding: 2px 5px;
  border-radius: 5px;
  color: #d63384;
}

.content pre {
  background-color: rgba(0, 86, 179, 0.1);
  padding: 10px;
  border-radius: 10px;
  overflow: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.content blockquote {
  margin: 10px 0;
  padding: 10px 20px;
  background-color: rgba(22, 114, 60, 0.1);
  border-left: 5px solid #16723c;
  color: #555;
}

.content ul,
.content ol {
  margin: 10px 0 10px 20px;
}

.content ul li,
.content ol li {
  margin: 5px 0;
}

/* 响应式设计 */
@media (min-width: 600px) {
  .markdown-component {
    flex-direction: row;
  }
  .sidebar {
    width: 250px;
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
  }
  .content {
    margin-left: 260px;
  }
}

@media (max-width: 600px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
    box-shadow: none;
  }
  .content {
    margin: 20px 0;
  }
}
</style>
