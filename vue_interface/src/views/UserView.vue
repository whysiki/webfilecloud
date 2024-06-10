<template>
  <div class="return-button">
    <n-button round size="small" @click="goBack">Return</n-button>
  </div>
  <div class="background-box">
    <n-card>
      <n-space align="center">
        <n-avatar round :src="userAvatar" alt="User Avatar" size="huge" />
        <h2>{{ username }}</h2>
        <n-button round size="small" @click="uploadAvatar">Upload Avatar</n-button>
        <input
          type="file"
          ref="fileInput"
          style="display: none"
          @change="handleAvatarChange"
        />
      </n-space>
    </n-card>
    <n-card>
      <template #header>
        <span>Statistics</span>
      </template>
      <FileTypeChart :typesCount="typesCount" />
      <FileSizeChart :allFilesSize="allFilesSize" :typesSizeCount="typesSizeCount" />
    </n-card>
  </div>
  <AlertComponent ref="alertPopup" />
</template>

<script>
import axios from "../axios";
import { NAvatar, NCard, NButton, NSpace } from "naive-ui";
import store from "../store";
import FileTypeChart from "../components/FileTypeChart.vue";
import FileSizeChart from "../components/FileSizeChart.vue";

export default {
  components: {
    NAvatar,
    NButton,
    NCard,
    NSpace,
    FileTypeChart,
    FileSizeChart,
  },
  data() {
    return {
      userAvatar: localStorage.getItem("userAvatar")
        ? localStorage.getItem("userAvatar")
        : null,
      username: store.state.username || localStorage.getItem("username") || null,
      token: store.state.token || localStorage.getItem("token") || null,
    };
  },
  async created() {
    await this.fetchAvatar();
  },
  computed: {
    files() {
      return store.state.files;
    },
    typesCount() {
      return this.files.reduce((acc, file) => {
        acc[file.file_type] = acc[file.file_type] ? acc[file.file_type] + 1 : 1;
        return acc;
      }, {});
    },
    allFilesSize() {
      let allfileSize = 0;
      this.files.forEach((file) => {
        const fileSize = parseFloat(file.file_size);
        if (!isNaN(fileSize)) {
          allfileSize += fileSize;
        }
      });
      return allfileSize;
    },
    typesSizeCount() {
      return this.files.reduce((acc, file) => {
        acc[file.file_type] = acc[file.file_type]
          ? acc[file.file_type] + parseFloat(file.file_size) //file.file_size is string
          : parseFloat(file.file_size);
        return acc;
      }, {});
    },
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    async fetchAvatar() {
      try {
        const response = await axios.get("/users/profileimage", {
          headers: {
            Authorization: `Bearer ${this.token}`,
            "Content-Type": "application/octet-stream",
          },
          responseType: "blob",
        });
        this.userAvatar = URL.createObjectURL(new Blob([response.data]));
        localStorage.setItem("userAvatar", this.userAvatar);
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
    uploadAvatar() {
      this.$refs.fileInput.click();
    },
    async handleAvatarChange(event) {
      const file = event.target.files[0];
      const formData = new FormData();
      formData.append("file", file);
      try {
        await axios.post("/users/upload/profileimage", formData, {
          headers: {
            Authorization: `Bearer ${this.token}`,
            "Content-Type": "multipart/form-data",
          },
        });
        await this.fetchAvatar();
        await this.$refs.alertPopup.showAlert("Update userAvatar successful");
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
  },
};
</script>

<style scoped>
@import "./css/UserView.css";
.return-button {
  position: absolute;
  top: 10px;
  left: 0px;
}
</style>
