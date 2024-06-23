<!-- DeleteUserComponent.vue -->
<template>
  <button
    class="top-bar-icon-button deleteUser"
    @click="confirmDeleteUser"
    title="Delete User"
  >
    <i class="fa-solid fa-user-slash"></i>
  </button>
  <!-- the below is global register components -->
  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>

<script>
import { ref } from "vue";
import axios from "../../axios"; // 导入 axios 实例
// import eventBus from "../../eventBus"; // 导入事件总线

export default {
  name: "DeleteUserComponent",
  setup() {
    const popInputRef = ref(null); // 使用 ref 来获取组件引用
    const alertPopup = ref(null);

    const deleteUser = async (password) => {
      try {
        const username = localStorage.getItem("username");
        const userin = {
          username: username,
          password: password,
        };
        const headers = {};

        const getIdResponse = await axios.post("/users/getid", userin, {
          headers: headers,
        });

        const userId = getIdResponse.data.id;

        await axios.delete("/users/delete", {
          params: {
            id: userId,
          },
        });
        // this.$router.push("/");
        window.location.href = "/";
      } catch (error) {
        if (error.response) {
          await alertPopup.value.showAlert(`Error: ${error.response.data.detail}`);
        } else if (error.request) {
          await alertPopup.value.showAlert("Error: No response from server");
        } else {
          await alertPopup.value.showAlert("Error", error.message);
        }
      }
    };

    const confirmDeleteUser = async () => {
      const tag = await alertPopup.value.showAlert(
        "Are you sure you want to delete your account?"
      );
      if (tag === "ok") {
        const password = await popInputRef.value
          .popInput("Password")
          .then((inputValue) => {
            return inputValue;
          })
          .catch((error) => {
            return error;
          });
        if (typeof password === "string" && password !== "") {
          await deleteUser(password);
        } else {
          await alertPopup.value.showAlert("Password is invalid");
        }
      }
    };

    return {
      confirmDeleteUser,
      popInputRef,
      alertPopup,
    };
  },
};
</script>
