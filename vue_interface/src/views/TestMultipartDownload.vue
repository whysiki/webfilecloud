<template>
  <div class="container">
    <h1>Multi-Threaded Download Test</h1>
    <h3>Input the a bucket name</h3>
    <input
      v-model="bucketName"
      type="text"
      placeholder="Bucket Name (default: filecloud)"
    />
    <h3>Input the object name</h3>
    <input v-model="objectName" type="text" placeholder="Object Name" />
    <h3>Enter the API address</h3>
    <input
      v-model="apiAddress"
      type="text"
      placeholder="API Address (default http://localhost:8000)"
    />
    <h3>Select the number of threads</h3>
    <input
      v-model.number="threadCount"
      type="number"
      placeholder="Number of Threads (default 10)"
      min="1"
    />
    <button @click="startDownload">Start Download</button>
    <div v-html="output"></div>
    <progress :value="totalProgress" max="100"></progress>
  </div>
  <div class="container">
    <h1>History Uploaded Objects</h1>
    <h3>(Store in localStorage)</h3>
    <div v-if="historyUploadedObjects.length > 0" class="historyUploadedObjects">
      <div
        class="historyUploadedObject"
        v-for="(historyUploadedObject, index) in historyUploadedObjects"
        :key="index"
      >
        <p>File Id: {{ historyUploadedObject.file_id }}</p>
        <p>Bucket Name: {{ historyUploadedObject.bucket_name }}</p>
        <p>Object Name: {{ historyUploadedObject.filename }}</p>
        <p>API Address: {{ historyUploadedObject.apiAddress }}</p>
        <p>Thread Count: {{ historyUploadedObject.threadCount }}</p>
        <p>Time: {{ historyUploadedObject.time }}</p>
        <p>Upload Time: {{ historyUploadedObject.uploadtime }} seconds</p>
        <!-- mutipartUploadedFiles.push({
          file_id: fileId,
          filename: file.name,
          bucket_name: this.bucketName,
          apiAddress: apiInput,
          threadCount: chunks,
          uploadtime: uploadTimeInSeconds,
          time: new Date().toLocaleString(),
        }); -->
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      bucketName: "filecloud",
      objectName: "",
      apiAddress: "http://localhost:8000",
      threadCount: 10,
      output: "",
      totalProgress: 0,
      // historyUploadedObjects: [],
    };
  },
  computed: {
    historyUploadedObjects() {
      return JSON.parse(localStorage.getItem("mutipartUploadedFiles")) || [];
    },
  },
  methods: {
    async startDownload() {
      const { bucketName, objectName, apiAddress, threadCount } = this;
      this.output = "Starting download...";
      this.totalProgress = 0;

      if (!bucketName || !objectName || !apiAddress || !threadCount) {
        alert("Please fill all fields correctly.");
        return;
      }

      try {
        const fileSizeResponse = await fetch(
          `${apiAddress}/file/download/${encodeURIComponent(
            bucketName
          )}/${encodeURIComponent(objectName)}`,
          {
            method: "HEAD",
          }
        );

        if (!fileSizeResponse.ok) {
          this.output = "Failed to get file size.";
          return;
        }

        const fileSize = parseInt(fileSizeResponse.headers.get("Content-Length"), 10);
        const chunkSize = Math.ceil(fileSize / threadCount);
        this.output = `File size: ${fileSize} bytes<br>Chunk size: ${chunkSize} bytes per thread<br><br>`;

        const chunks = [];
        for (let i = 0; i < threadCount; i++) {
          const start = i * chunkSize;
          const end = Math.min((i + 1) * chunkSize - 1, fileSize - 1);
          chunks.push({ start, end });
        }

        const downloadChunk = async (start, end, index) => {
          const rangeHeader = `bytes=${start}-${end}`;
          const response = await fetch(
            `${apiAddress}/file/download/${encodeURIComponent(
              bucketName
            )}/${encodeURIComponent(objectName)}`,
            {
              headers: {
                Range: rangeHeader,
              },
            }
          );

          if (!response.ok) {
            throw new Error(`Failed to download chunk ${index}`);
          }

          const blob = await response.blob();
          return { index, blob };
        };

        const downloadChunks = async () => {
          const promises = chunks.map(async (chunk, index) => {
            try {
              const result = await downloadChunk(chunk.start, chunk.end, index);
              // Calculate progress based on number of chunks completed
              this.totalProgress = ((index + 1) / threadCount) * 100;
              return { index, blob: result.blob, success: true };
            } catch (error) {
              return { index, success: false };
            }
          });

          const results = await Promise.all(promises);
          return results;
        };

        const results = await downloadChunks();
        results.sort((a, b) => a.index - b.index);
        const orderedBlobs = results.map((result) => result.blob);
        const combinedBlob = new Blob(orderedBlobs);
        const url = URL.createObjectURL(combinedBlob);
        const a = document.createElement("a");
        a.href = url;
        a.download = objectName;
        a.textContent = "Download completed file";
        this.output += `<br>${a.outerHTML}`;
      } catch (error) {
        this.output = `Error: ${error.message}`;
      }
    },
  },
};
</script>

<style scoped>
.container {
  width: 80%;
  margin: 20px auto;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(176, 43, 43, 0.1);
  text-align: center;
}

.container h1 {
  color: #1a7be3;
  margin-bottom: 20px;
}

.container input {
  width: calc(100% - 20px);
  margin: 10px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 10px;
  font-size: 16px;
}

.container button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}

.container button:hover {
  background-color: #16723c;
}

.container progress {
  width: 100%;
  height: 20px;
  margin-top: 10px;
}

.historyUploadedObjects {
  width: 100%;
  margin: 10px auto;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(176, 43, 43, 0.1);
}

.historyUploadedObject {
  margin-bottom: 20px;
  padding: 10px;
  border: 2px solid #3498db;
  border-radius: 10px;
}

.historyUploadedObjects p {
  margin: 5px 0;
}

.historyUploadedObjects p:first-child {
  font-weight: bold;
}

.historyUploadedObjects p:nth-child(odd) {
  background-color: #f0f0f0;
  padding: 5px;
  border-radius: 10px;
}

.historyUploadedObjects p:nth-child(even) {
  padding: 5px;
}

.historyUploadedObjects p:last-child {
  color: green;
  font-weight: bold;
}
progress {
  width: 100%;
  height: 20px;
  border: none;
  border-radius: 10px;
  appearance: none;
  background-color: #f0f0f0;
}

progress::-webkit-progress-bar {
  background-color: #f0f0f0;
  border-radius: 10px;
}

progress::-webkit-progress-value {
  background-color: #3498db;
  border-radius: 10px;
}

progress::-moz-progress-bar {
  background-color: #3498db;
  border-radius: 10px;
}
</style>
