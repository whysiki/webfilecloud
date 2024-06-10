<template>
  <n-space vertical>
    <n-switch v-model:value="toPreviewFile" size="large"> Preview File </n-switch>
    <n-button type="error" @click="clearCache"> Clear Cache </n-button>
  </n-space>
</template>

<script>
import { ref } from "vue";
import { useStore } from "vuex";
import store from "../store";

export default {
  name: "SettingsComponent",
  setup() {
    const toPreviewFile = ref(store.state.toPreviewFile);
    const clearCache = () => {
      localStorage.clear();
      // Add any additional cache clearing logic here
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
};
</script>
