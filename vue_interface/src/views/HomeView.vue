<template>
  <div>
    <div class="home">
      <router-link to="/">
        <i class="fas fa-home home-icon"></i>
      </router-link>
    </div>
    <AuthComponent />
  </div>
</template>

<script>
import AuthComponent from "../components/AuthComponent.vue";

export default {
  name: "HomeView",
  components: {
    AuthComponent,
  },
};
</script>

<style scoped>
.home {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.home-icon {
  font-size: 50px;
  color: #007bff;
}
</style>
