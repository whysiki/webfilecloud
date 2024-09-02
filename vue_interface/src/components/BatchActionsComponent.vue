<!-- BatchActionsComponent.vue -->
<template>
  <div class="batch-actions" v-if="showBatchActions">
    <progress
      max="100"
      :value="batchProgress"
      class="batch-actions-progress"
      v-if="batchProgress > 0 && batchProgress < 100"
    ></progress>
    <button
      @click="batchMove"
      class="batch-actions-button batch-actions-button-move"
    >
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
    <button
      @click="batchDelete"
      class="batch-actions-button batch-actions-button-delete"
    >
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
    <button
      @click="selectAllFiles"
      class="batch-actions-button batch-actions-button-select-all"
    >
      <i class="fas fa-check-square"></i>
      <span class="batch-actions-button-text">SelectAll</span>
    </button>
    <button
      @click="cancelAllRequests"
      class="batch-actions-button batch-actions-button-cancel"
      v-if="
        (batchProgress > 0 && batchProgress < 100) || cancelTokens.length > 0
      "
    >
      <i class="fa-solid fa-ban"></i>
      <span class="batch-actions-button-text">CancelAll</span>
    </button>
  </div>
  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>
<script>
import axios from "../axios";
import store from "../store";
import eventBus from "../eventBus";
import axiosModule from "axios";
export default {
  data() {
    return {
      cancelTokens: [],
    };
  },
  computed: {
    showBatchActions() {
      return store.state.selectedFiles.length > 0;
    },
    batchProgress() {
      return store.state.batchProgress;
    },
  },
  methods: {
    selectAllFiles() {
      store.state.selectedFiles = [...store.state.files];
      eventBus.emit("select-all-files");
    },
    clearSelectedFiles() {
      store.state.selectedFiles = [];
      eventBus.emit("clear-selected-files");
    },
    async batchDelete() {
      const tag = await this.$refs.alertPopup.showAlert(
        "Are you sure you want to delete those files?"
      );
      if (tag === "ok") {
        const total = store.state.selectedFiles.length;
        let count = 0;
        const deletePromises = store.state.selectedFiles.map(async (file) => {
          try {
            const source = axiosModule.CancelToken.source();
            this.cancelTokens.push(source);
            await axios.delete(`/files/delete?file_id=${file.id}`, {
              cancelToken: source.token,
            });
            count++;
            store.state.batchProgress = (count / total) * 100;
          } catch (error) {
            console.error(
              `Error deleting file: ${
                error.response?.data?.detail || error.message
              }`
            );
          }
        });
        await Promise.all(deletePromises);
        await this.$refs.alertPopup.showAlert("Delete completed");
        eventBus.emit("batch-files-deleted");
      }
    },
    async batchDownload() {
      const tag = await this.$refs.alertPopup.showAlert(
        "Are you sure you want to download those files?"
      );
      if (tag === "ok") {
        const total = store.state.selectedFiles.length;
        let count = 0;
        const downloadPromises = store.state.selectedFiles.map(async (file) => {
          try {
            const source = axiosModule.CancelToken.source();
            this.cancelTokens.push(source);
            file.showdownloadProgressBar = true;
            const response = await axios.get(
              `/files/download/stream?file_id=${file.id}`,
              {
                responseType: "blob",
                onDownloadProgress: (progressEvent) => {
                  file.downloadProgress = Math.round(
                    (progressEvent.loaded * 100) / file.file_size
                  );
                },
                // cancelToken: file.cancelTokenSource.token,
                cancelToken: source.token,
              }
            );
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute("download", file.filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            count++;
            store.state.batchProgress = (count / total) * 100;
          } catch (error) {
            await this.$refs.alertPopup.showAlert(
              `Error downloading file: ${
                error.response?.data?.detail || error.message
              }`
            );
          } finally {
            file.showdownloadProgressBar = false;
          }
        });
        await Promise.all(downloadPromises);
        await this.$refs.alertPopup.showAlert("Download completed");
      }
    },
    async batchMove() {
      const tag = await this.$refs.alertPopup.showAlert(
        "Are you sure you want to move this file? (enter '/' to move to root directory)"
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
          const newNodesArray = newNodes
            .split("/")
            .filter((node) => node !== "");
          const newNodesArrayStr = JSON.stringify(newNodesArray);
          const total = store.state.selectedFiles.length;
          let count = 0;
          const movePromises = store.state.selectedFiles.map(async (file) => {
            try {
              const source = axiosModule.CancelToken.source();
              this.cancelTokens.push(source);
              await axios.post(
                `/file/modifynodes?file_nodes=${newNodesArrayStr}&file_id=${file.id}`,
                {},
                {
                  cancelToken: source.token,
                }
              );
              count++;
              store.state.batchProgress = (count / total) * 100;
            } catch (error) {
              console.error(
                `Error moving file: ${
                  error.response?.data?.detail || error.message
                }`
              );
            }
          });
          await Promise.all(movePromises);
          await this.$refs.alertPopup.showAlert("Move completed");
          eventBus.emit("batch-files-moved");
        } else {
          await this.$refs.alertPopup.showAlert("New file path is invalid");
        }
      }
    },
    cancelAllRequests() {
      this.cancelTokens.forEach((source) => {
        source.cancel("Operation canceled by the user.");
      });
      this.cancelTokens = [];
      store.state.batchProgress = 0;
      eventBus.emit("cancel-all-requests");
    },
  },
};
</script>

<style scoped>
@import "./css/BatchActionsComponent.css";
</style>
