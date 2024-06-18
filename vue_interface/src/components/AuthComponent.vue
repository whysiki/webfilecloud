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

        store.commit("setToken", response.data.access_token);

        store.commit("setUserName", this.username);

        localStorage.setItem("refresh_token", response.data.refresh_token);

        this.$router.push("/filelist");
      } catch (error) {
        if (error.response) {
          // 请求已发送，服务器返回了一个非 2xx 的状态码
          await this.$refs.alertPopup.showAlert(
            `Error: ${error.response.data.detail}`
          ); // 显示错误信息
        } else if (error.request) {
          // 请求已发送，但没有收到响应
          await this.$refs.alertPopup.showAlert(
            "Error: No response from server"
          ); // 显示错误信息
        } else {
          // 设置请求时发生了错误
          await this.$refs.alertPopup.showAlert("Error", error.message); // 显示错误信息
        }
      }
    },
    async register() {
      try {
        // 使用 axios 发送 POST 请求，注册新用户
        const response = await axios.post("/users/register", {
          // 请求体中包含 username 和 password 字段
          username: this.username,
          password: this.password,
        });
        // 如果请求成功，显示成功信息
        await this.$refs.alertPopup.showAlert(
          `User ${response.data.username} created successfully.`
        );
        // ID: ${response.data.id}
        // this.username = "";
        // this.password = "";
      } catch (error) {
        // 如果请求失败，显示错误信息
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
