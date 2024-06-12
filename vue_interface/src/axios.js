import axios from "axios";
// import store from "./store";

const instance = axios.create({
  // 基础 URL 会被添加到所有请求的 URL 前面
  baseURL: "http://47.115.43.139:8000",
  headers: {
    // 设置 Content-Type 请求头为 'application/json'
    "Content-Type": "application/json",
  },
});

export default instance;
