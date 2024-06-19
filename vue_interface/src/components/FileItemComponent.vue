<!-- FileItemComponent.vue -->
<template>
  <div
    class="file-item"
    title="Click to expand details"
    :style="listStyle"
    @mouseover="mouseovershowfileCardDetails"
    @mouseleave="mouseleaveshowfileCardDetails"
  >
    <!-- 文件卡片头部  显示文件�? -->
    <div class="file-card-header">
      <!-- 复选框 -->
      <input
        type="checkbox"
        v-model="selected"
        @change="toggleSelect"
        class="selected-file"
      />
      <!-- 文件�? -->
      <div class="file-header" @click.prevent="toggleDetails">
        <div
          class="file-name"
          v-if="!isEditingFilename"
          @dblclick.prevent="editFilename"
        >
          <p class="long-text">{{ file.filename }}</p>
        </div>
        <input
          class="file-rename-input"
          type="text"
          v-else
          v-model="newFilename"
          @blur="updateFilename"
          @keyup.enter="updateFilename"
          title="Press Enter a new filename and press Enter to save"
          @mouseleave="updateFilename"
        />
      </div>
    </div>
    <!-- 文件详细  显示文件详细信息和文件预�?  点击文件名展开 -->
    <div v-if="showfileCardDetails" class="file-card-details">
      <p>Owner name: {{ file.file_owner_name }}</p>
      <p>Upload time: {{ file.file_create_time }}</p>
      <p>File size: {{ formatSize(file.file_size) }}</p>
      <p>File path: {{ parseNodes(file.file_nodes) }}</p>
      <p>File type: {{ file.file_type }}</p>
      <p class="long-text" v-if="copyError">
        Download link: {{ downloadLink }}
      </p>
      <p class="long-text" v-if="copyError">Preview link: {{ previewLink }}</p>
      <!-- 复制按钮 -->
      <div class="file-card-details-buttons">
        <button
          @click="copyToClipboard(downloadLink)"
          class="file-card-details-button"
          title="Click to copy direct download link to clipboard"
        >
          📋<i class="fas fa-download"></i>
        </button>
        <button
          @click="copyToClipboard(previewLink)"
          class="file-card-details-button"
          title="Click to copy preview link to clipboard"
        >
          📋<i class="fas fa-stream"></i>
        </button>
      </div>
      <!-- 文件操作按钮 -->
      <div class="file-item-button-container" v-if="!isCardView">
        <button
          @click.prevent="confirmMovefile(file.id)"
          class="file-button"
          v-if="toShowSingleFileItemControlButton"
          title="Click to move file"
        >
          <i class="fas fa-folder-plus"></i>
        </button>
        <button
          @click.prevent="downloadFile(file)"
          class="file-button"
          v-if="toShowSingleFileItemControlButton"
          title="Click to download file"
        >
          <i class="fas fa-download"></i>
        </button>
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
          <i class="fas fa-times"></i>
        </button>
        <button
          @click.prevent="confirmDeleteFile(file.id, file.filename)"
          class="file-button delete-file"
          title="Click to delete file"
          v-if="toShowSingleFileItemControlButton"
        >
          <i class="fas fa-trash"></i>
        </button>
        <button
          @click.prevent="editFilename"
          class="rename-button"
          id="rename-button-single-file"
          title="Click to rename file or cancel renaming"
        >
          <i class="fas fa-edit"></i>
        </button>
        <router-link
          :to="`/preview/${file.id}/${file.file_type}/${encodeURIComponent(previewLink)}`"
        >
          <a
            class="preview-button"
            id="preview-button-single-file"
            title="Click to preview file image or video or text"
            @click.stop
          >
            <i class="fas fa-eye"></i>
          </a>
        </router-link>
        <a
          :href="downloadLink"
          download
          class="download-button"
          @click.stop
          title="Click to direct download file"
        >
          <i class="fas fa-download"></i>
        </a>
      </div>

      <!-- 文件预览 容器 -->
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
        <!-- <img
          :src="fileImageUrl"
          alt="Image preview"
          class="file-preview video-preview"
          v-else-if="isVideoFile && fileImageUrl"
        /> -->
        <img
          :src="fileImageUrl"
          alt="Image preview"
          class="file-preview image-preview"
          v-else-if="isImageFile && fileImageUrl"
        />
      </div>
    </div>
    <!-- 下载进度�? -->
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
import eventBus from "../eventBus";

export default {
  props: {
    file: {
      type: Object,
      required: true,
    },
    viewMode: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      showfileCardDetails: false,
      selected: false,
      fileImageUrl: null,
      fileContent: null,
      isEditingFilename: false,
      copyError: false,
      newFilename: "",
    };
  },

  computed: {
    // 监听事件
    events() {
      return [
        {
          name: "expand-all",
          handler: () => {
            this.showfileCardDetails = true;
          },
        },
        {
          name: "collapse-all",
          handler: () => {
            this.showfileCardDetails = false;
          },
        },
        {
          name: "clear-selected-files",
          handler: () => {
            this.selected = false;
          },
        },
        {
          name: "select-all-files",
          handler: () => {
            this.selected = true;
          },
        },
        {
          name: "cancel-all-requests",
          handler: () => {
            this.showdownloadProgressBar = false;
          },
        },
      ];
    },
    toShowSingleFileItemControlButton() {
      return store.state.toShowSingleFileItemControlButton;
    },
    previewLink() {
      return store.state.baseUrl + this.file.file_download_link;
    },
    downloadLink() {
      return (store.state.baseUrl + this.file.file_download_link).replace(
        "/file/download",
        "/file/directdownload"
      );
    },
    listStyle() {
      if (this.viewMode === "card") {
        //统一卡片大小
        return {
          width: "280px",
          // height: "35vh",
        };
      } else {
        return {};
      }
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
    isShowPreview() {
      return store.state.toPreviewFile;
    },
    previewFileSize() {
      if (
        store.state.previewFileSize &&
        typeof store.state.previewFileSize === "number" &&
        store.state.previewFileSize > 0
      ) {
        //单位mb
        return store.state.previewFileSize;
      } else {
        return 10;
      }
    },
  },
  mounted() {
    this.eventHandlers = this.events.map((event) => {
      eventBus.on(event.name, event.handler);
      return event;
    });
  },
  beforeUnmount() {
    this.eventHandlers.forEach((event) =>
      eventBus.off(event.name, event.handler)
    );
    if (store.state.selectedFiles.includes(this.file)) {
      store.commit("removeSelectedFile", this.file);
    }
  },
  watch: {
    file: {
      immediate: true,
      handler(newFile) {
        // console.log("previewFileSize", this.previewFileSize);
        // console.log("previewFileSizetype", typeof this.previewFileSize);
        if (newFile && this.isShowPreview) {
          if (newFile.file_size > 1024 * 1024 * this.previewFileSize) {
            this.fileContent = null;
            this.fileImageUrl = null;
          } else if (this.isTextFile) {
            // 文本文件
            this.getFileContent(newFile).then((content) => {
              this.fileContent = content;
            });
          } else if (this.isImageFile) {
            // 图片文件
            this.createImageUrl(newFile).then((url) => {
              this.fileImageUrl = url;
            });
          } else if (this.isVideoFile) {
            // 视频文件
            this.createVideoUrl(newFile).then((url) => {
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
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        await this.$refs.alertPopup.showAlert(
          "Copied to clipboard successfully"
        );
        this.copyError = false;
      } catch (err) {
        await this.$refs.alertPopup.showAlert("Error copying to clipboard");
        await this.$refs.alertPopup.showAlert(err);
        // await this.$refs.alertPopup.showAlert(text);
        this.copyError = true;
      }
    },
    mouseleaveshowfileCardDetails() {
      if (store.state.toMouseEventFileItem) {
        this.showfileCardDetails = false;
      }
    },
    mouseovershowfileCardDetails() {
      if (store.state.toMouseEventFileItem) {
        this.showfileCardDetails = true;
      }
    },
    toggleSelect() {
      if (this.selected) {
        store.commit("addSelectedFile", this.file);
      } else {
        store.commit("removeSelectedFile", this.file);
      }
    },
    toggleDetails() {
      this.showfileCardDetails = !this.showfileCardDetails;
      this.copyError = false;
    },
    editFilename() {
      this.isEditingFilename = !this.isEditingFilename;
      this.newFilename = this.file.filename;
    },
    async updateFilename() {
      try {
        await axios.post(
          `/file/modifyname?file_id=${this.file.id}&new_file_name=${this.newFilename}`,
          {},
          {}
        );
        this.isEditingFilename = false;
        eventBus.emit("one-file-updated");
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(
            `Error updating filename: ${error.response.data.detail}`
          );
        } else {
          await this.$refs.alertPopup.showAlert("No response from server");
        }
      }
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
        file.cancelTokenSource = axiosModule.CancelToken.source();
        const response = await axios.get(
          `/files/download/stream?file_id=${file.id}`,
          {
            responseType: "blob",
            onDownloadProgress: (progressEvent) => {
              file.downloadProgress = Math.round(
                (progressEvent.loaded * 100) / file.file_size
              );
            },
            cancelToken: file.cancelTokenSource.token,
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
      } catch (error) {
        if (axiosModule.isCancel(error)) {
          await this.$refs.alertPopup.showAlert(
            `Download cancelled: ${error.message}`
          );
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
        await axios.delete(`/files/delete?file_id=${fileId}`, {});
        this.$refs.alertPopup.showAlert("File deleted successfully");
        eventBus.emit("one-file-deleted");
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
          const newNodesArray = newNodes
            .split("/")
            .filter((node) => node !== "");
          const newNodesArrayStr = JSON.stringify(newNodesArray);
          await this.moveFile(file_id, newNodesArrayStr);
        } else {
          await this.$refs.alertPopup.showAlert("New file path is invalid");
        }
      }
    },
    async moveFile(file_id, newNodesArrayStr) {
      try {
        await axios.post(
          `/file/modifynodes?file_nodes=${newNodesArrayStr}&file_id=${file_id}`,
          {},
          {}
        );
        await this.$refs.alertPopup.showAlert("File moved successfully");
        eventBus.emit("one-file-moved");
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
        const response = await axios.get(
          `/files/img/preview?file_id=${file.id}`,
          {
            headers: {
              "Content-Type": "application/octet-stream",
            },
            responseType: "blob",
          }
        );
        // console.log("img preview");
        const url = window.URL.createObjectURL(new Blob([response.data]));
        return url;
      } catch (error) {
        await this.$refs.alertPopup.showAlert(
          `Error creating image URL: ${error.message}`
        );
        return null;
      }
    },

    async createVideoUrl(file) {
      try {
        const response = await axios.get(
          `/files/video/preview?file_id=${file.id}`,
          {
            headers: {
              "Content-Type": "application/octet-stream",
            },
            responseType: "blob",
          }
        );
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
        const response = await axios.get(`/files/download?file_id=${file.id}`, {
          headers: {
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
