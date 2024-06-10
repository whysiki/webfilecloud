<!-- FileItemComponent.vue -->
<template>
  <div class="file-item" title="Click to expand details" :style="listStyle">
    <!-- @mouseover="showfileCardDetails = true" -->
    <!-- @mouseleave="showfileCardDetails = false" -->
    <input
      type="checkbox"
      v-model="selected"
      @change="toggleSelect"
      class="selected-file"
    />
    <div class="file-header" @click.prevent="toggleDetails">
      <div class="file-name">{{ file.filename }}</div>
      <div class="file-item-button-container" v-if="!isCardView">
        <button @click.prevent="confirmMovefile(file.id)" class="file-button">
          Move
        </button>
        <button @click.prevent="downloadFile(file)" class="file-button">Download</button>
        <button
          v-if="
            file.downloadProgress > 0 &&
            file.downloadProgress < 100 &&
            file.showdownloadProgressBar
          "
          @click.prevent="cancelDownload(file)"
          class="file-button cancel-download"
          title="Click to cancel download"
        >
          Cancel
        </button>
        <button
          @click.prevent="confirmDeleteFile(file.id, file.filename)"
          class="file-button delete-file"
          title="Click to delete file"
        >
          Delete
        </button>
        <a
          :href="downloadLink"
          download
          class="preview-button"
          id="preview-button-single-file"
          @click.stop
        >
          <i class="fas fa-eye"></i>
        </a>
      </div>
    </div>
    <div v-if="showfileCardDetails" class="file-card-details">
      <p>Owner name: {{ file.file_owner_name }}</p>
      <p>Upload time: {{ file.file_create_time }}</p>
      <p>File size: {{ formatSize(file.file_size) }}</p>
      <p>File path: {{ parseNodes(file.file_nodes) }}</p>

      <div class="file-preview-container">
        <textarea
          v-if="isTextFile && fileContent"
          :value="fileContent"
          readonly
          class="file-preview"
        ></textarea>
        <video
          v-else-if="isVideoFile && fileImageUrl"
          :src="fileImageUrl"
          controls
          class="file-preview video-preview"
        ></video>
        <img
          :src="fileImageUrl"
          alt="Image preview"
          class="file-preview image-preview"
          v-else-if="isImageFile && fileImageUrl"
        />
      </div>
    </div>
    <div
      v-show="file.showdownloadProgressBar"
      class="progress-bar-container"
      v-if="file.downloadProgress > 0 && file.downloadProgress < 100"
    >
      <progress
        max="100"
        :value="file.downloadProgress"
        class="download-progress-bar"
      ></progress>
      <span class="progress-text">{{ file.downloadProgress }}%</span>
    </div>
  </div>
  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>

<script>
import axios from "../axios"; // 导入 axios 实例
import axiosModule from "axios";
import store from "../store";
export default {
  props: ["file"],
  data() {
    return {
      showfileCardDetails: false,
      selected: false,
      fileImageUrl: null,
      fileContent: null,
    };
  },

  computed: {
    downloadLink() {
      return store.state.baseUrl + this.file.file_download_link;
    },
    listStyle() {
      if (store.state.viewMode === "card") {
        //统一卡片大小
        return {
          width: "280px",
          margin: "5px",
        };
      } else {
        return {};
      }
    },
    viewMode() {
      return store.state.viewMode;
    },
    isCardView() {
      return this.viewMode === "card";
    },
    isTextFile() {
      return [
        "txt",
        "md",
        "json",
        "js",
        "html",
        "css",
        "py",
        "java",
        "c",
        "cpp",
        "h",
        "hpp",
        "sql",
        "sh",
        "conf",
        "bat",
      ].includes(this.file.file_type);
    },
    isVideoFile() {
      return ["mp4", "webm", "ogg", "mkv"].includes(this.file.file_type);
    },
    isImageFile() {
      return ["jpg", "png", "jpeg"].includes(this.file.file_type);
    },
  },
  mounted() {
    this.emitter.on("expand-all", () => {
      this.showfileCardDetails = true;
    });
    this.emitter.on("collapse-all", () => {
      this.showfileCardDetails = false;
    });
    this.emitter.on("clear-selected-files", () => {
      this.selected = false;
    });
    this.emitter.on("select-all-files", () => {
      this.selected = true;
    });
    this.emitter.on("cancel-all-requests", () => {
      this.showdownloadProgressBar = false;
    });
  },
  beforeUnmount() {
    this.emitter.off("expand-all");
    this.emitter.off("collapse-all");
    this.emitter.off("clear-selected-files");
    this.emitter.off("select-all-files");
    this.emitter.off("cancel-all-requests");
    if (store.state.selectedFiles.includes(this.file)) {
      store.commit("removeSelectedFile", this.file);
    }
  },
  watch: {
    file: {
      immediate: true,
      handler(newFile) {
        if (newFile) {
          if (newFile.file_size > 1024 * 1024 * 10) {
            this.fileContent = null;
            this.fileImageUrl = null;
          } else if (this.isTextFile) {
            this.getFileContent(newFile).then((content) => {
              this.fileContent = content;
            });
          } else if (this.isImageFile || this.isVideoFile) {
            this.createImageUrl(newFile).then((url) => {
              this.fileImageUrl = url;
            });
          }
        } else {
          this.fileContent = null;
          this.fileImageUrl = null;
        }
      },
    },
  },
  methods: {
    toggleSelect() {
      if (this.selected) {
        store.commit("addSelectedFile", this.file);
      } else {
        store.commit("removeSelectedFile", this.file);
      }
    },
    toggleDetails() {
      this.showfileCardDetails = !this.showfileCardDetails;
    },
    formatSize(size) {
      if (size < 1024) {
        return `${size} B`;
      } else if (size < 1024 * 1024) {
        return `${(size / 1024).toFixed(2)} KB`;
      } else {
        return `${(size / 1024 / 1024).toFixed(2)} MB`;
      }
    },
    parseNodes(file_nodes) {
      return file_nodes.length > 0 ? "/" + file_nodes.join("/") : "/";
    },
    async downloadFile(file) {
      try {
        file.showdownloadProgressBar = true;
        const token = localStorage.getItem("token");
        file.cancelTokenSource = axiosModule.CancelToken.source();
        const response = await axios.get(`/files/download/stream?file_id=${file.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: "blob",
          onDownloadProgress: (progressEvent) => {
            file.downloadProgress = Math.round(
              (progressEvent.loaded * 100) / file.file_size
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
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        if (axiosModule.isCancel(error)) {
          await this.$refs.alertPopup.showAlert(`Download cancelled: ${error.message}`);
        } else {
          await this.$refs.alertPopup.showAlert(
            `Error downloading file: ${error.message}`
          );
        }
      } finally {
        file.showdownloadProgressBar = false;
      }
    },

    cancelDownload(file) {
      if (file.cancelTokenSource) {
        file.cancelTokenSource.cancel("User cancelled the download");
      }
    },
    async confirmDeleteFile(fileId, filename) {
      const tag = await this.$refs.alertPopup.showAlert(
        `Are you sure you want to delete ${filename}?`
      );
      if (tag === "ok") {
        await this.deleteFile(fileId);
      }
    },
    async deleteFile(fileId) {
      try {
        const token = localStorage.getItem("token");
        await axios.delete(`/files/delete?file_id=${fileId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.$refs.alertPopup.showAlert("File deleted successfully");
        this.emitter.emit("one-file-deleted");
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(
            `Error deleting file: ${error.response.data.detail}`
          );
        } else {
          await this.$refs.alertPopup.showAlert("No response from server");
        }
      }
    },
    async confirmMovefile(file_id) {
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
          await this.moveFile(file_id, newNodesArrayStr);
        } else {
          await this.$refs.alertPopup.showAlert("New file path is invalid");
        }
      }
    },
    async moveFile(file_id, newNodesArrayStr) {
      try {
        const token = localStorage.getItem("token");
        await axios.post(
          `/file/modifynodes?file_nodes=${newNodesArrayStr}&file_id=${file_id}`,
          {},
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        await this.$refs.alertPopup.showAlert("File moved successfully");
        this.emitter.emit("one-file-moved");
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(
            `Error moving file: ${error.response.data.detail}`
          );
        } else {
          await this.$refs.alertPopup.showAlert("No response from server");
        }
      }
    },

    async createImageUrl(file) {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`/files/download?file_id=${file.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/octet-stream",
          },
          responseType: "blob",
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        return url;
      } catch (error) {
        await this.$refs.alertPopup.showAlert(
          `Error creating image URL: ${error.message}`
        );
        return null;
      }
    },

    async readAsText(blob, encoding = "UTF-8") {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => resolve(event.target.result);
        reader.onerror = (error) => reject(error);
        reader.readAsText(blob, encoding);
      });
    },
    async getFileContent(file) {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(`/files/download?file_id=${file.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/octet-stream",
          },
          responseType: "blob",
        });
        const content = await this.readAsText(response.data);
        return content;
      } catch {
        return null;
      }
    },
  },
};
</script>

<style scoped>
@import "./css/FileItemComponent.css";
</style>
