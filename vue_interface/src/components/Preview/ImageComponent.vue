<template>
  <div>
    <div class="image-container"><img :src="imageUrl" /></div>
  </div>
</template>

<script>
export default {
  props: {
    imageUrl: {
      type: String,
      required: true,
    },
  },
};
</script>
<style scoped>
.image-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.image-container,
.image-container img {
  width: 100%;
  height: 100%;
}
</style>
