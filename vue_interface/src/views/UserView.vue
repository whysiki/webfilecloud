<template>
  <div class="user-view">
    <!-- 用户信息 -->
    <div class="user-info">
      <img class="user-avatar" :src="userAvatar" alt="User Avatar" />
      <h2 class="user-name">{{ userName }}</h2>
    </div>
    <!-- 用户文件统计 -->
    <div class="user-stats">
      <div class="stat-item">
        <i class="fas fa-file"></i>
        <span>{{ fileCount }}</span>
      </div>
      <div class="stat-item">
        <i class="fas fa-folder"></i>
        <span>{{ fileTypeCount }}</span>
      </div>
    </div>
    <!-- 设置界面 -->
    <div class="settings">
      <h3>Settings</h3>
      <div class="setting-item">
        <label for="preview-toggle">Preview Waiting:</label>
        <input type="checkbox" id="preview-toggle" v-model="previewWaiting" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      id: null,
      userName: "User Name",
      userAvatar: "../../../fastapi_backend/whysiki.jpg",
      fileCount: 0,
      fileTypeCount: 0,
      previewWaiting: false,
    };
  },
  created() {
    this.id = this.$route.params.id;
  },
};
</script>

<style scoped></style>
