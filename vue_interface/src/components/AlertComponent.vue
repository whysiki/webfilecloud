<template>
  <div class="alert-container" v-if="isshowAlert">
    <div class="alert">
      <p>{{ alertMessage }}</p>
      <div class="button-container-alert">
        <button class="alert-button handleOk" @click="handleOk">OK</button>
        <button class="alert-button handleCancel" @click="handleCancel">Cancel</button>
        <button class="alert-button handleHome" @click="handleHome">Home</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isshowAlert: false,
      alertMessage: "",
      resolvePromise: null,
      autoCloseTimeout: null,
    };
  },
  methods: {
    showAlert(message, autoCloseTime) {
      this.alertMessage = message;
      this.isshowAlert = true;

      this.autoCloseTimeout = setTimeout(
        () => {
          this.handleCancel();
        },
        autoCloseTime && typeof autoCloseTime === "number" ? autoCloseTime : 10000
      );

      // 返回一个 Promise，用于处理用户的选择
      return new Promise((resolve) => {
        this.resolvePromise = resolve;
      });
    },
    hideAlert() {
      this.isshowAlert = false;
      this.resolvePromise = null;
    },
    handleOk() {
      if (this.resolvePromise) {
        this.resolvePromise("ok"); // 返回 "ok"
      }
      this.hideAlert();
    },
    handleCancel() {
      if (this.resolvePromise) {
        this.resolvePromise("cancel"); // 返回 "cancel"
      }
      this.hideAlert();
    },
    handleHome() {
      this.isshowAlert = false;
      this.$router.push("/");
    },
  },
};
</script>

<style scoped>
@import "./css/AlertComponent.css";
</style>
