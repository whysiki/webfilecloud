<template>
  <router-view></router-view>
  <router-view name="filelist"></router-view>
  <RollPage />
</template>

<script>
import RollPage from "./components/PageControl/RollPage.vue";
export default {
  name: "App",
  components: {
    RollPage,
  },
};
</script>
