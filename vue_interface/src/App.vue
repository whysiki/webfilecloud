<template>
  <div id="app">
    <router-view v-slot="{ Component, route }">
      <keep-alive :include="cachedComponents" :exclude="excludedComponents">
        <component :is="Component" :key="route.fullPath" />
      </keep-alive>
    </router-view>
    <RollPage />
  </div>
</template>

<script>
import RollPage from "./components/PageControl/RollPage.vue";

export default {
  name: "App",
  components: {
    RollPage,
  },
  data() {
    return {
      cachedComponents: ["HomeView", "FileListView", "UserView", "FileFolderView"],
      excludedComponents: ["PreviewPage"],
    };
  },
};
</script>
