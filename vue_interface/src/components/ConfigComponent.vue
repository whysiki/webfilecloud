<template>
  <div class="settings-container">
    <div class="setting-item">
      <span class="setting-label"
        >Preview File
        <span
          :class="{ 'text-green': toPreviewFile, 'text-red': !toPreviewFile }"
        >
          {{ istoPreviewFile }}
        </span></span
      >
      <n-switch v-model:value="toPreviewFile" class="setting-switch"></n-switch>
    </div>
    <div class="setting-item">
      <span class="setting-label"
        >MouseEventFileItem
        <span
          :class="{
            'text-green': toMouseEventFileItem,
            'text-red': !toMouseEventFileItem,
          }"
        >
          {{ istoMouseEventFileItem }}
        </span></span
      >
      <n-switch
        v-model:value="toMouseEventFileItem"
        class="setting-switch"
      ></n-switch>
    </div>
    <div class="setting-item">
      <span class="setting-label"
        >FileItemControlButton
        <span
          :class="{
            'text-green': toShowSingleFileItemControlButton,
            'text-red': !toShowSingleFileItemControlButton,
          }"
        >
          {{ istoShowSingleFileItemControlButton }}
        </span></span
      >
      <n-switch
        v-model:value="toShowSingleFileItemControlButton"
        class="setting-switch"
      ></n-switch>
    </div>
    <div class="setting-item">
      <span class="setting-label">
        Preview File Size
        <span
          :class="{
            'text-green': whatpreviewFileSize < 50,
            'text-red': whatpreviewFileSize >= 50,
          }"
          >{{ whatpreviewFileSize }}</span
        >
      </span>
      <n-input
        v-model:value="previewFileSize"
        class="setting-input"
        type="number"
      ></n-input>
    </div>
    <n-button
      class="setting-button"
      @click="clearCache"
      title="Clear LocalStorage"
      >Clear LocalStorage</n-button
    >
    <n-button
      class="setting-button"
      @click="clearStore"
      title="Clear LocalStorage"
      >Clear store</n-button
    >
  </div>
</template>

<script>
import { ref } from "vue";
import store from "../store";
import { NButton, NSwitch, NInput } from "naive-ui";
export default {
  components: {
    NButton,
    NSwitch,
    NInput,
  },
  setup() {
    const previewFileSize = ref(store.state.previewFileSize);
    const toPreviewFile = ref(store.state.toPreviewFile);
    const toMouseEventFileItem = ref(store.state.toMouseEventFileItem);
    const toShowSingleFileItemControlButton = ref(
      store.state.toShowSingleFileItemControlButton
    );
    const clearCache = () => {
      localStorage.clear();
    };
    const clearStore = () => {
      store.commit("clearStore");
    };

    return {
      toPreviewFile,
      toMouseEventFileItem,
      toShowSingleFileItemControlButton,
      clearCache,
      clearStore,
      previewFileSize,
    };
  },
  watch: {
    previewFileSize(newVal) {
      //类型转为数字
      store.commit("setPreviewFileSize", Number(newVal));
    },
    toPreviewFile(newVal) {
      store.commit("setToPreviewFile", newVal);
    },
    toMouseEventFileItem(newVal) {
      store.commit("setToMouseEventFileItem", newVal);
    },
    toShowSingleFileItemControlButton(newVal) {
      store.commit("setToShowSingleFileItemControlButton", newVal);
    },
  },
  computed: {
    whatpreviewFileSize() {
      return store.state.previewFileSize;
    },
    istoPreviewFile() {
      return store.state.toPreviewFile;
    },
    istoMouseEventFileItem() {
      return store.state.toMouseEventFileItem;
    },
    istoShowSingleFileItemControlButton() {
      return store.state.toShowSingleFileItemControlButton;
    },
  },
};
</script>

<style scoped>
.setting-input {
  margin-left: auto;
  border: 2px solid #3498db;
  width: 100px;
  border-radius: 20px;
}
</style>
