<template>
  <div>
    <h1>
      Chunked File Upload <span>{{ bucketName }}</span>
    </h1>
    <input type="file" ref="fileInput" multiple />
    <h3>Enter API address default(http://127.0.0.1:8000)</h3>
    <input
      type="text"
      v-model="apiInput"
      placeholder="Enter API address default(http://127.0.0.1:8000)"
    />
    <progress
      id="progressBar"
      max="100"
      :value="progress"
      class="upload-progress"
      v-if="progress > 0 && progress < 100"
    ></progress>

    <!-- </div> -->
    <button @click="uploadFile">Upload</button>

    <p>{{ informationP2 }}</p>
    <p>{{ informationP }}</p>
    <p>{{ informationP3 }}</p>
    <p id="informationError">{{ informationError }}</p>
    <p>{{ uploadTime }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      apiInput: "http://127.0.0.1:8000",
      progress: 0,
      informationP2: "",
      informationP: "",
      informationP3: "",
      informationError: "",
      uploadTime: "",
      bucketName: "filecloud",
    };
  },
  methods: {
    async uploadFile() {
      const apiInput = this.apiInput.trim() || "http://127.0.0.1:8000";
      if (!apiInput) {
        alert("Please enter API address.");
        return;
      }
      const fileInput = this.$refs.fileInput;
      const files = fileInput.files;
      if (files.length === 0) {
        alert("Please select a file.");
        return;
      }
      const file = files[0];
      const chunkSize = 10 * 1024 * 1024; // 10 MB
      const chunks = Math.ceil(file.size / chunkSize);
      const fileId = this.uuidv4();
      let order = 0;
      this.progress = 0;
      const startTime = new Date();

      const uploadChunk = async (start, end, order) => {
        const blob = file.slice(start, end);
        const chunkFormData = new FormData();
        chunkFormData.append("upload_file", blob);
        this.informationP2 = `chunk size : ${end - start} <br> current chunk : ${order}`;
        try {
          const response = await fetch(
            `${apiInput}/upload?file_id=${fileId}&order=${order}`,
            {
              method: "POST",
              body: chunkFormData,
            }
          );
          if (!response.ok) {
            this.informationError = `Failed to upload chunk ${order + 1}`;
            throw new Error(`Failed to upload chunk ${order + 1}`);
          }
          this.informationP = `Uploaded chunk: ${order}`;
          const chunkProgress = (1 / chunks) * 100;
          this.progress += chunkProgress;
        } catch (error) {
          this.informationError = `Failed to upload chunk ${order + 1}`;
          throw error;
        }
      };

      const chunkPromises = [];
      this.progress = 0;
      for (let i = 0; i < chunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(file.size, start + chunkSize);
        chunkPromises.push(uploadChunk(start, end, order));
        order++;
      }

      try {
        await Promise.all(chunkPromises);
        const mergeResponse = await fetch(
          `${apiInput}/merge?filename=${encodeURIComponent(
            file.name
          )}&file_id=${fileId}&bucket_name=${this.bucketName}`,
          {
            method: "POST",
          }
        );
        if (!mergeResponse.ok) {
          this.informationError = "Failed to merge chunks";
          throw new Error("Failed to merge chunks");
        }
        const endTime = new Date();
        const uploadTime = endTime - startTime;
        const uploadTimeInSeconds = (uploadTime / 1000).toFixed(2);
        this.uploadTime = `Upload Time: ${uploadTimeInSeconds} seconds`;
        this.informationP3 = `File uploaded successfully! <br> File ID: ${fileId} <br> Filename: ${file.name} <br> Bucket Name: ${this.bucketName}`;
        const mutipartUploadedFiles = JSON.parse(
          localStorage.getItem("mutipartUploadedFiles") || "[]"
        );
        mutipartUploadedFiles.push({
          file_id: fileId,
          filename: file.name,
          bucket_name: this.bucketName,
          apiAddress: apiInput,
          threadCount: chunks,
          uploadtime: uploadTimeInSeconds,
          time: new Date().toLocaleString(),
        });
        localStorage.setItem(
          "mutipartUploadedFiles",
          JSON.stringify(mutipartUploadedFiles)
        );
      } catch (error) {
        console.error(error);
      } finally {
        this.progress = 0;
      }
    },
    uuidv4() {
      return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        const r = (Math.random() * 16) | 0,
          v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
      });
    },
  },
};
</script>

<style scoped>
div {
  width: 80%;
  margin: 20px auto;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(176, 43, 43, 0.1);
  text-align: center;
}

div h1 {
  color: #1a7be3;
  margin-bottom: 20px;
}

div input[type="file"] {
  margin: 10px;
}

div input[type="text"] {
  width: calc(100% - 20px);
  margin: 10px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 10px;
  font-size: 16px;
}

div #progressBar {
  width: 100%;
  height: 20px;
  background-color: #f0f0f0;
  border-radius: 5px;
  overflow: hidden;
  margin: 10px auto;
}

div #progressBar div {
  height: 100%;
  width: 0;
  background-color: #3498db;
  border-radius: 10px;
}

div button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

div button:hover {
  background-color: #16723c;
}

div p {
  margin-top: 10px;
  font-size: 14px;
}

div #informationError {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

div #uploadTime {
  color: green;
  font-weight: bold;
  margin-top: 10px;
}
</style>
