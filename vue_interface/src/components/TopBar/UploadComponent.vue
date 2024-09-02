<template>
  <button
    @click="toggleUploadFileForm"
    class="top-bar-icon-button uploadFile"
    title="Upload File"
  >
    <i class="fas fa-upload"></i>
  </button>
  <form v-if="showUploadFileForm" @submit.prevent="uploadFiles" class="form-uploadFile">
    <div class="form-uploadFile-group">
      <input
        type="file"
        @change="handleFilesUpload"
        required
        class="form-uploadFile-input"
        multiple
      />
    </div>
    <button type="submit" class="form-uploadFile-button">Upload File</button>
    <button @click.prevent="showPopInput" class="form-uploadFile-button">
      Modify Upload Path. Current: {{ currentUploadStrPath }}
    </button>
    <progress
      max="100"
      :value="uploadProgress"
      class="form-uploadFile-progress-bar"
      v-show="showProgressBar"
    ></progress>
  </form>
  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>

<script>
import CryptoJS from "crypto-js";
import axios from "../../axios";
import eventBus from "../../eventBus";
export default {
  name: "UploadComponent",
  data() {
    return {
      files: [],
      showUploadFileForm: false,
      uploadProgress: 0,
      showProgressBar: false,
      inputUploadStrNodes: "",
      completedFiles: 0,
    };
  },
  computed: {
    currentUploadStrNodes() {
      return this.inputUploadStrNodes.length > 0
        ? this.inputUploadStrNodes
        : localStorage.getItem("currentNodes");
    },
    currentUploadStrPath() {
      const Nodes = JSON.parse(this.currentUploadStrNodes);
      let path = "";
      for (let i = 0; i < Nodes.length; i++) {
        path += Nodes[i];
        if (i !== Nodes.length - 1) {
          path += "/";
        }
      }
      return path === "" || path == "[]" ? "Root" : path;
    },
  },
  mounted() {
    eventBus.on("update-current-nodes", this.updateInputUploadStrNodes);
    window.addEventListener("scroll", this.handleScroll);
  },
  beforeUnmount() {
    eventBus.off("update-current-nodes", this.updateInputUploadStrNodes);
    window.removeEventListener("scroll", this.handleScroll);
  },
  methods: {
    handleFilesUpload(event) {
      this.files = Array.from(event.target.files);
    },
    updateInputUploadStrNodes(value) {
      this.inputUploadStrNodes = value;
    },
    async showPopInput() {
      await this.$refs.popInputRef
        .popInput("Upload Path")
        .then((inputValue) => {
          const nodes = inputValue.split("/");
          const currentUploadStrNodes = JSON.stringify(nodes);
          this.inputUploadStrNodes = currentUploadStrNodes;
        })
        .catch(() => {
          this.inputUploadStrNodes = "";
        });
    },
    handleScroll() {
      if (window.scrollY > 15) {
        this.showUploadFileForm = false;
      }
    },
    toggleUploadFileForm() {
      this.showUploadFileForm = !this.showUploadFileForm;
    },
    async uploadSingleFile(file, totalFiles) {
      const reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.onload = async () => {
        let fileId = "";
        if (file.size <= 1024 * 1024 * 100) {
          const username = localStorage.getItem("username");
          const arrayBuffer = reader.result;
          const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
          const fileHash = CryptoJS.SHA256(wordArray).toString();
          const usernameHash = CryptoJS.SHA1(username).toString();
          const file_nodes_array = JSON.parse(this.currentUploadStrNodes);
          const file_nodes_hash = CryptoJS.SHA1(file_nodes_array.join("")).toString();
          fileId = fileHash + usernameHash + file_nodes_hash;
        } else {
          await this.$refs.alertPopup.showAlert(
            `File ${file.name} is too large to upload. The digest check existence will not be computed`,
            1000
          );
        }
        const formData = new FormData();
        formData.append("file", file);
        try {
          this.showProgressBar = true;
          await axios.post(
            `/files/upload?file_id=${fileId}&file_nodes=${this.currentUploadStrNodes}`,
            formData,
            {
              headers: {
                "Content-Type": "multipart/form-data",
              },
              onUploadProgress: (progressEvent) => {
                const fileProgress = Math.round(
                  (progressEvent.loaded * 100) / progressEvent.total
                );
                this.uploadProgress = Math.round(
                  ((this.completedFiles + fileProgress / 100) * 100) / totalFiles
                );
              },
            }
          );
          this.completedFiles += 1;
          await this.$refs.alertPopup.showAlert(
            `File ${file.name} uploaded successfully in ${this.currentUploadStrPath}`,
            1000
          );
          eventBus.emit("file-uploaded");
        } catch (error) {
          this.completedFiles += 1;
          if (error.response) {
            await this.$refs.alertPopup.showAlert(
              `Error uploading file ${file.name}: ${error.response.data.detail}`,
              1000
            );
          } else if (error.request) {
            await this.$refs.alertPopup.showAlert(
              `Error uploading file ${file.name}: No response from server`,
              1000
            );
          } else {
            await this.$refs.alertPopup.showAlert(
              `Error uploading file ${file.name}: ${error.message}`,
              1000
            );
          }
        } finally {
          if (this.completedFiles === totalFiles) {
            this.showProgressBar = false;
            this.completedFiles = 0;
            await this.$refs.alertPopup.showAlert(
              "All files uploaded successfully",
              1000
            );
          }
        }
      };
    },
    async uploadFiles() {
      const totalFiles = this.files.length;
      const uploadPromises = this.files.map((file) => {
        return this.uploadSingleFile(file, totalFiles);
      });
      await Promise.all(uploadPromises);
    },
  },
};
</script>
