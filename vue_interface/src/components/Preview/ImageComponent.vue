<template>
  <div v-if="isLoading" class="loader-container">
    <div class="loader"></div>
  </div>
  <div class="image-container" v-show="!isLoading">
    <img :src="imageUrl" @load="handleImageLoad" @error="handleImageError" />
  </div>
</template>

<script>
import { ref, watch } from "vue";

export default {
  props: {
    imageUrl: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const isLoading = ref(true);

    const handleImageLoad = () => {
      isLoading.value = false;
    };

    const handleImageError = () => {
      console.error("Failed to load image.");
      isLoading.value = false;
    };

    // Watch for changes to imageUrl and reset loading state
    watch(
      () => props.imageUrl,
      () => {
        isLoading.value = true;
      }
    );

    return {
      isLoading,
      handleImageLoad,
      handleImageError,
    };
  },
};
</script>

<style scoped>
/* 图片容器样式 */
.image-container {
  background-color: #000; /* 背景颜色 */
  width: 100%;
  /*  确保容器占满整个视窗高度 */
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  overflow: hidden; /* 避免滚动条 */
  /* 动画 */
  animation: fadeIn 0.5s ease-in-out;
}

.image-container img {
  max-width: 100%; /* 确保图片不会超出容器宽度 */
  max-height: 100%; /* 确保图片不会超出容器高度 */
  object-fit: contain; /* 保持图片比例，包含在容器内 */
  transition: transform 0.3s ease; /* 添加过渡效果 */
}

/* 图片悬停放大效果 */
.image-container img:hover {
  transform: scale(1.05); /* 放大图片 */
}

/* 滚动条样式 */
.image-container::-webkit-scrollbar {
  width: 8px; /* 滚动条宽度 */
}

.image-container::-webkit-scrollbar-thumb {
  background-color: #888; /* 滚动条颜色 */
  border-radius: 4px; /* 滚动条圆角 */
}

.image-container::-webkit-scrollbar-thumb:hover {
  background-color: #555; /* 滚动条悬停颜色 */
}
</style>
