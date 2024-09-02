<template>
  <button class="scroll-to-top" @click="scrollToTop" v-show="showScrollButton">
    ↑
  </button>
  <button
    class="scroll-to-bottom"
    @click="scrollToBottom"
    v-show="showScrollButton"
  >
    ↓
  </button>
</template>

<script>
export default {
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
    scrollToBottom() {
      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    },
  },
};
</script>

<style screen>
.scroll-to-top,
.scroll-to-bottom {
  position: fixed;
  right: 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.5s;
}

.scroll-to-top {
  bottom: 130px;
}

.scroll-to-bottom {
  bottom: 70px;
}

.scroll-to-top:hover,
.scroll-to-bottom:hover {
  background-color: #16723c;
}

@media (max-width: 600px) {
  .scroll-to-top,
  .scroll-to-bottom {
    right: 0px;
  }
}
</style>
