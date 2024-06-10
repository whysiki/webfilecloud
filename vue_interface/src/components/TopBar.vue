<template>
  <div class="top-bar">
    <div class="return-home" title="Return to home page">
      <router-link to="/">
        <i class="fas fa-home"></i>
      </router-link>
    </div>
    <button class="top-bar-icon-button search" @click="toggleSearch" title="Search">
      <i class="fas fa-search"></i>
    </button>
    <button
      @click="toggleUploadFileForm"
      class="top-bar-icon-button uploadFile"
      title="Upload File"
    >
      <i class="fas fa-upload"></i>
    </button>
    <button
      class="top-bar-icon-button deleteAll"
      @click="confirmDeleteAllFiles"
      title="Delete All Files"
    >
      <i class="fa-solid fa-trash"></i>
    </button>
    <button
      class="top-bar-icon-button deleteUser"
      @click="confirmDeleteUser"
      title="Delete User"
    >
      <i class="fa-solid fa-user-slash"></i>
    </button>
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
  <PopInputComponent ref="popInputRef" />
  <AlertComponent ref="alertPopup" />
</template>

<script>
import CryptoJS from "crypto-js";
import axios from "../axios"; // 导入 axios 实例
export default {
  name: "SideBar",
  components: {},
  data() {
    return {
      files: [], // 初始化 files 数据属性
      file: null, // 初始化 file 数据属性
      showUploadFileForm: false, // 初始化 UploadFile 数据属性
      uploadProgress: 0, // 初始化 uploadProgress 数据属性
      showProgressBar: false, // 初始化 showProgressBar 数据属性
      inputUploadStrNodes: "",
      showSearch: false,
      // oldCurrentNodes: [],
      completedFiles: 0,
    };
  },
  computed: {
    currentUploadStrNodes() {
      //这是数组的字符串表示
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
    this.emitter.on("update-current-nodes", this.updateInputUploadStrNodes);
    window.addEventListener("scroll", this.handleScroll);
  },
  beforeUnmount() {
    this.emitter.off("update-current-nodes", this.updateInputUploadStrNodes);
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
          // console.log("用户输入:", inputValue);
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
            `File ${file.name} is too large to upload. The digest check existence will not be computed`
          );
        }
        const formData = new FormData();
        formData.append("file", file);
        try {
          this.showProgressBar = true;
          const token = localStorage.getItem("token");
          await axios.post(
            `/files/upload?file_id=${fileId}&file_nodes=${this.currentUploadStrNodes}`,
            formData,
            {
              headers: {
                Authorization: `Bearer ${token}`,
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
          this.emitter.emit("file-uploaded");
        } catch (error) {
          this.completedFiles += 1;
          if (error.response) {
            await this.$refs.alertPopup.showAlert(
              `Error uploading file ${file.name}: ${error.response.data.detail}`,
              2000
            );
          } else if (error.request) {
            await this.$refs.alertPopup.showAlert(
              `Error uploading file ${file.name}: No response from server`,
              2000
            );
          } else {
            await this.$refs.alertPopup.showAlert(
              `Error uploading file ${file.name}: ${error.message}`,
              2000
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
        return this.uploadSingleFile(file, totalFiles); // Add 'return' here
      });
      await Promise.all(uploadPromises);
    },

    async confirmDeleteUser() {
      const tag = await this.$refs.alertPopup.showAlert(
        "Are you sure you want to delete your account? " //Your need to enter your password after clicking OK.
      );
      if (tag === "ok") {
        const password = await this.$refs.popInputRef
          .popInput("Password")
          .then((inputValue) => {
            return inputValue;
          })
          .catch((error) => {
            return error;
          });
        if (typeof password === "string" && password !== "") {
          await this.deleteUser(password);
        } else {
          await this.$refs.alertPopup.showAlert("Password is invalid");
        }
      }
    },
    async deleteUser(password) {
      try {
        const token = localStorage.getItem("token");
        const username = localStorage.getItem("username");
        const userin = {
          username: username,
          password: password,
        };
        const headers = {
          Authorization: `Bearer ${token}`,
        };

        const getIdResponse = await axios.post("/users/getid", userin, {
          headers: headers,
        });

        const userId = getIdResponse.data.id;

        await axios.delete("/users/delete", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          params: {
            id: userId,
          },
        });
        this.$router.push("/");
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(`Error: ${error.response.data.detail}`);
        } else if (error.request) {
          await this.$refs.alertPopup.showAlert("Error: No response from server");
        } else {
          await this.$refs.alertPopup.showAlert("Error", error.message);
        }
      }
    },

    toggleSearch() {
      this.emitter.emit("toggle-search", !this.showSearch);
      this.showSearch = !this.showSearch;
    },
    async confirmDeleteAllFiles() {
      //进制基数，这里为 10，表示将字符串作为十进制数解析。
      const currentFilesLength = parseInt(localStorage.getItem("currentFilesLength"), 10);
      console.log(currentFilesLength);
      if (
        currentFilesLength === 0 ||
        currentFilesLength === null ||
        currentFilesLength === undefined
      ) {
        this.$refs.alertPopup.showAlert("No files to delete");
      } else {
        const tag = await this.$refs.alertPopup.showAlert(
          "Are you sure you want to delete all files?"
        );
        if (tag === "ok") {
          await this.deleteAllFiles();
        }
      }
    },
    async deleteAllFiles() {
      try {
        const token = localStorage.getItem("token");
        await axios.delete("/users/files/delete", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.$refs.alertPopup.showAlert("All files deleted successfully"); // 显示文件删除成功的信息
      } catch (error) {
        if (error.response) {
          await this.$refs.alertPopup.showAlert(`Error: ${error.response.data.detail}`);
        } else if (error.request) {
          await this.$refs.alertPopup.showAlert("Error: No response from server");
        } else {
          await this.$refs.alertPopup.showAlert("Error", error.message);
        }
      } finally {
        this.emitter.emit("all-files-deleted");
      }
    },
  },
};
</script>

<style>
/*，使用 scoped 属性确保样式只在组件内部生效。 */
@import "./css/TopBar.css";
</style>
