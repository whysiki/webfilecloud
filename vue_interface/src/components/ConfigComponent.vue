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
import { NButton, NSwitch } from "naive-ui";
export default {
  components: {
    NButton,
    NSwitch,
  },
  setup() {
    const toPreviewFile = ref(store.state.toPreviewFile);
    const toMouseEventFileItem = ref(store.state.toMouseEventFileItem);
    const clearCache = () => {
      localStorage.clear();
    };
    const clearStore = () => {
      store.commit("clearStore");
    };

    return {
      toPreviewFile,
      toMouseEventFileItem,
      clearCache,
      clearStore,
    };
  },
  watch: {
    toPreviewFile(newVal) {
      store.commit("setToPreviewFile", newVal);
    },
    toMouseEventFileItem(newVal) {
      store.commit("setToMouseEventFileItem", newVal);
    },
  },
  computed: {
    istoPreviewFile() {
      return store.state.toPreviewFile;
    },
    istoMouseEventFileItem() {
      return store.state.toMouseEventFileItem;
    },
  },
};
</script>
