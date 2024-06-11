<template>
  <div class="settings-container">
    <div class="setting-item">
      <span class="setting-label">Preview File {{ istoPreviewFile }}</span>
      <n-switch v-model:value="toPreviewFile" class="setting-switch"></n-switch>
    </div>
    <n-button
      class="setting-button file-button"
      id="setting-button-clear-cache"
      @click="clearCache"
    >
      Clear Cache
    </n-button>
  </div>
</template>

<script>
import { ref } from "vue";
import store from "../store";
import { NButton, NSwitch } from "naive-ui";
export default {
  components: {
    // NSpace,
    NButton,
    NSwitch,
  },
  setup() {
    const toPreviewFile = ref(store.state.toPreviewFile);
    const clearCache = () => {
      localStorage.clear();
    };

    return {
      toPreviewFile,
      clearCache,
    };
  },
  watch: {
    toPreviewFile(newVal) {
      store.commit("setToPreviewFile", newVal);
    },
  },
  computed: {
    istoPreviewFile() {
      return store.state.toPreviewFile;
    },
  },
};
</script>

<style scoped>
.settings-container {
  width: 100%;
  margin: 20px auto;
  padding: 20px;
  /* background-color: rgba(255, 255, 255, 0.5); */
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(176, 43, 43, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.setting-label {
  font-size: 16px;
  color: #333;
  font-weight: bold;
  margin-right: 10px;
}

.setting-switch {
  margin-left: auto;
}

.setting-button {
  width: 120px;
  height: 40px;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  background-color: #3498db;
  transition: background-color 0.3s ease;
}

/* .setting-button:hover { */
/* background-color: #16723c; */
/* } */

#setting-button-clear-cache {
  display: block;
}
</style>
