<template>
  <div class="top-bar">
    <div class="return-home" title="Return to home page">
      <router-link to="/">
        <i class="fas fa-home"></i>
      </router-link>
    </div>
    <SearchComponent />
    <button
      @click="toggleUploadFileForm"
      class="top-bar-icon-button uploadFile"
      title="Upload File"
    >
      <i class="fas fa-upload"></i>
    </button>
    <DeleteAllComponent />
    <DeleteUserComponent />
  </div>
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
      Modify Upload Path. Current : {{ currentUploadStrPath }}
    </button>
    <progress
      max="100"
      :value="uploadProgress"
      class="form-uploadFile-progress-bar"
      v-show="showProgressBar"
    ></progress>
  </form>
  <!-- the below is global register components -->
  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>

<script>
import CryptoJS from "crypto-js";
import axios from "../axios"; // 导入 axios 实例
import eventBus from "../eventBus";
import SearchComponent from "./TopBar/SearchComponent.vue";
import DeleteAllComponent from "./TopBar/DeleteAllComponent.vue";
import DeleteUserComponent from "./TopBar/DeleteUserComponent.vue";
export default {
  name: "TopBar",
  components: {
    SearchComponent,
    DeleteAllComponent,
    DeleteUserComponent,
  },
  data() {
    return {
      files: [], // 初始化 files 数据属性
      file: null, // 初始化 file 数据属性
      showUploadFileForm: false, // 初始化 UploadFile 数据属性
      uploadProgress: 0, // 初始化 uploadProgress 数据属性
      showProgressBar: false, // 初始化 showProgressBar 数据属性
      inputUploadStrNodes: "",
      completedFiles: 0,
    };
  },
  computed: {
    currentUploadStrNodes() {
      //这是数组的字符串表示，用于上传文件时的路径
      return this.inputUploadStrNodes.length > 0
        ? this.inputUploadStrNodes
        : localStorage.getItem("currentNodes");
    },
    currentUploadStrPath() {
      //这是路径的字符串表示，根据当前节点数组currentUploadStrNodes生成
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
      this.files = Array.from(event.target.files); // 将用户选择的文件赋值给 this.files
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
        .catch((error) => {
          console.log(error);
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
    handleFileUpload(event) {
      // 定义 handleFileUpload 方法
      this.file = event.target.files[0]; // 将用户选择的文件赋值给 this.file
    },
    async uploadSingleFile(file, totalFiles) {
      const reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.onload = async () => {
        let fileId = "";
        if (file.size <= 1024 * 1024 * 100) {
          // 100MB
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

<style>
@import "./css/TopBar.css";
</style>
