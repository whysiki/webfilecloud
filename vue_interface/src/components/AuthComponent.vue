<template>
  <form class="login-form">
    <div class="login-form__group">
      <label for="username" class="login-form__label">Username:</label>
      <input
        type="text"
        v-model="username"
        required
        minlength="3"
        class="login-form__input"
      />
    </div>
    <div class="login-form__group">
      <label for="password" class="login-form__label">Password:</label>
      <input
        type="password"
        v-model="password"
        required
        minlength="8"
        class="login-form__input"
      />
    </div>
    <div class="login-form__button-group">
      <button
        type="button"
        @click="login"
        class="login-form__button login-form__button--login"
      >
        Login
      </button>
      <button
        type="button"
        @click="register"
        class="login-form__button login-form__button--register"
      >
        Register
      </button>
    </div>
  </form>
  <AlertComponent ref="alertPopup" />
</template>

<script>
import axios from "../axios"; // 导入 axios 实例
import store from "../store"; // 导入 store
export default {
  components: {},
  data() {
    return {
      username: "",
      password: "",
      isLogin: true,
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post("/users/login", {
          username: this.username,
          password: this.password,
        });
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("username", this.username);
        localStorage.setItem("currentNodes", "[]");
        store.commit("setUserName", this.username);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        this.$router.push("/filelist");
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(
            `Error: ${error.response.data.detail}`
          );
        } else if (error.request) {
          await this.$refs.alertPopup.showAlert(
            "Error: No response from server"
          );
        } else {
          await this.$refs.alertPopup.showAlert("Error", error.message);
        }
      }
    },
    async register() {
      try {
        const response = await axios.post("/users/register", {
          username: this.username,
          password: this.password,
        });
        await this.$refs.alertPopup.showAlert(
          `User ${response.data.username} created successfully.`
        );
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(
            `Error: ${error.response.data.detail}`
          );
        } else if (error.request) {
          await this.$refs.alertPopup.showAlert(
            "Error: No response from server"
          );
        } else {
          await this.$refs.alertPopup.showAlert("Error", error.message);
        }
      }
    },
  },
};
</script>

<style scoped>
@import "./css/AuthComponent.css";
</style>
