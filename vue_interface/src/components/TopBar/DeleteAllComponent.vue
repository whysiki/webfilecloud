<!-- DeleteAllComponent.vue -->
<template>
  <button
    class="top-bar-icon-button deleteAll"
    @click="confirmDeleteAllFiles"
    title="Delete All Files"
  >
    <i class="fa-solid fa-trash"></i>
  </button>
  <AlertComponent ref="alertPopup" />
</template>

<script>
import { ref } from "vue";
import axios from "../../axios"; // 导入 axios 实例
import eventBus from "../../eventBus.js"; // 导入事件总线

export default {
  name: "DeleteAllComponent",
  setup() {
    const alertPopup = ref(null);

    const confirmDeleteAllFiles = async () => {
      const currentFilesLength = parseInt(localStorage.getItem("currentFilesLength"), 10);
      if (
        currentFilesLength === 0 ||
        currentFilesLength === null ||
        currentFilesLength === undefined
      ) {
        await alertPopup.value.showAlert("No files to delete");
      } else {
        const tag = await alertPopup.value.showAlert(
          "Are you sure you want to delete all files?"
        );
        if (tag === "ok") {
          await deleteAllFiles();
        }
      }
    };

    const deleteAllFiles = async () => {
      try {
        await axios.delete("/users/files/delete", {
          headers: {},
        });
        await alertPopup.value.showAlert("All files deleted successfully");
      } catch (error) {
        if (error.response) {
          await alertPopup.value.showAlert(`Error: ${error.response.data.detail}`);
        } else if (error.request) {
          await alertPopup.value.showAlert("Error: No response from server");
        } else {
          await alertPopup.value.showAlert(`Error: ${error.message}`);
        }
      } finally {
        eventBus.emit("all-files-deleted");
      }
    };

    return {
      confirmDeleteAllFiles,
      alertPopup,
    };
  },
};
</script>
