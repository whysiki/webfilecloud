import { createStore } from "vuex";

export default createStore({
  state: {
    files: [],
    selectedFiles: [],
    batchProgress: 0,
    viewMode: "list",
    treePathList: [],
    // baseUrl: "http://localhost:8000",
    typesCount: {},
    typesSizeCount: {},
    allfileSize: 0,
    username: "",
    token: "",
    toPreviewFile: false,
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
    changeViewMode(state, mode) {
      state.viewMode = mode;
    },
    buildTreePathList(state, paths) {
      state.treePathList = paths;
    },
    setTypesCount(state, typesCount) {
      state.typesCount = typesCount;
    },
    setAllfileSize(state, allfileSize) {
      state.allfileSize = allfileSize;
    },
    setUserName(state, username) {
      state.username = username;
    },
    setToken(state, token) {
      state.token = token;
    },
    setTypesSizeCount(state, typesSizeCount) {
      state.typesSizeCount = typesSizeCount;
    },
    setToPreviewFile(state, toPreviewFile) {
      state.toPreviewFile = toPreviewFile;
    },
  },
});
