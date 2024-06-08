import { createStore } from "vuex";

export default createStore({
  state: {
    files: [],
    selectedFiles: [],
    batchProgress: 0,
  },
  mutations: {
    setFiles(state, files) {
      state.files = files;
    },
    addSelectedFile(state, file) {
      state.selectedFiles.push(file);
    },
    removeSelectedFile(state, file) {
      const index = state.selectedFiles.findIndex((f) => f.id === file.id);
      if (index !== -1) {
        state.selectedFiles.splice(index, 1);
      }
    },
  },
});
