<template>
  <div v-if="visible" class="pop-input-overlay">
    <div class="pop-input-container">
      <h3 class="pop-input-title">Please Input {{ inputContent }}</h3>
      <input v-model="inputValue" type="text" class="pop-input-field" />
      <div class="pop-input-button-container">
        <button @click="confirmInput" class="pop-input-button confirm-button">
          Confirm
        </button>
        <button @click="cancelInput" class="pop-input-button cancel-button">
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PopInputComponent",
  data() {
    return {
      inputContent: "Content",
      visible: false,
      inputValue: "",
      resolve: null,
      reject: null,
    };
  },
  methods: {
    popInput(inputContent) {
      if (inputContent) {
        this.inputContent = inputContent;
      }
      this.visible = true;
      this.inputValue = "";
      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    confirmInput() {
      if (this.resolve) {
        this.resolve(this.inputValue);
      }
      this.visible = false;
    },
    cancelInput() {
      if (this.reject) {
        this.reject(null);
      }
      this.visible = false;
    },
  },
};
</script>

<style scoped>
@import "./css/PopInputComponent.css";
</style>
