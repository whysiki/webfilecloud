<!-- BatchActionsComponent.vue -->
<template>
  <div class="batch-actions" v-if="showBatchActions">
    <button @click="batchMove" class="batch-actions-button batch-actions-button-move">
      <i class="fas fa-arrows-alt"></i>
      <span class="batch-actions-button-text">BatchMove</span>
    </button>
    <button
      @click="batchDownload"
      class="batch-actions-button batch-actions-button-download"
    >
      <i class="fas fa-download"></i>
      <span class="batch-actions-button-text">BatchDownload</span>
    </button>
    <button @click="batchDelete" class="batch-actions-button batch-actions-button-delete">
      <i class="fas fa-trash-alt"></i>
      <span class="batch-actions-button-text">BatchDelete</span>
    </button>
    <button
      @click="clearSelectedFiles"
      class="batch-actions-button batch-actions-button-clear"
    >
      <i class="fas fa-times"></i>
      <span class="batch-actions-button-text">ClearSelect</span>
    </button>
    <progress
      max="100"
      :value="batchProgress"
      class="batch-actions-progress"
      v-if="batchProgress > 0"
    >
      {{ batchProgress }}%
    </progress>
  </div>

  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>

<script>
import axios from "../axios";
import store from "../store";
import axiosModule from "axios";

export default {
  computed: {
    showBatchActions() {
      return store.state.selectedFiles.length > 0;
    },
    batchProgress() {
      return store.state.batchProgress;
    },
  },
  methods: {
    clearSelectedFiles() {
      store.state.selectedFiles = [];
    },
    async batchDelete() {
      const total = store.state.selectedFiles.length;
      let count = 0;
      for (let file of store.state.selectedFiles) {
        try {
          const token = localStorage.getItem("token");
          await axios.delete(`/files/delete?file_id=${file.id}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          count++;
          store.state.batchProgress = (count / total) * 100;
        } catch (error) {
          console.error(`Error deleting file: ${error.response.data.detail}`);
        }
      }
      await this.$refs.alertPopup.showAlert("Delete completed");
      this.emitter.emit("batch-files-deleted");
    },
    async batchDownload() {
      const total = store.state.selectedFiles.length;
      let count = 0;
      for (let file of store.state.selectedFiles) {
        try {
          file.showdownloadProgressBar = true;
          const token = localStorage.getItem("token");
          file.cancelTokenSource = axiosModule.CancelToken.source();
          const response = await axios.get(`/files/download?file_id=${file.id}`, {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/octet-stream",
            },
            responseType: "blob",
            onDownloadProgress: (progressEvent) => {
              file.downloadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
            },
            cancelToken: file.cancelTokenSource.token,
          });
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", file.filename);
          document.body.appendChild(link);
          link.click();
          count++;
          store.state.batchProgress = (count / total) * 100;
        } catch (error) {
          await this.$refs.alertPopup.showAlert(
            `Error downloading file: ${error.response.data.detail}`
          );
        }
      }
      await this.$refs.alertPopup.showAlert("Download completed");
    },

    async batchMove() {
      const tag = await this.$refs.alertPopup.showAlert(
        "Are you sure you want to move this file?(enter '/' to move to root directory)"
      );
      if (tag === "ok") {
        const newNodes = await this.$refs.popInputRef
          .popInput("New file path")
          .then((inputValue) => {
            return inputValue;
          })
          .catch((error) => {
            return error;
          });
        if (typeof newNodes === "string" && newNodes !== "") {
          const newNodesArray = newNodes.split("/").filter((node) => node !== "");
          const newNodesArrayStr = JSON.stringify(newNodesArray);
          const total = store.state.selectedFiles.length;
          let count = 0;
          for (let file of store.state.selectedFiles) {
            try {
              const token = localStorage.getItem("token");
              await axios.post(
                `/file/modifynodes?file_nodes=${newNodesArrayStr}&file_id=${file.id}`,
                {},
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                  },
                }
              );
              count++;
              store.state.batchProgress = (count / total) * 100;
            } catch (error) {
              console.error(`Error moving file: ${error.response.data.detail}`);
            }
          }
          await this.$refs.alertPopup.showAlert("Move completed");
          this.emitter.emit("batch-files-moved");
        }
      } else {
        await this.$refs.alertPopup.showAlert("New file path is invalid");
      }
    },
  },
};
</script>

<style scoped>
@import "./css/BatchActionsComponent.css";
</style>
