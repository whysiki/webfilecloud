import axios from "axios";

const BASE_URL = "http://localhost:8000";

const instance = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

function handleTokenRefreshFailure() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/";
}

//在请求头中加入token
instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    config.__retryCount = config.__retryCount || 0;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

//detail	"Could not validate credentials" status: 401
//detail	"Not authenticated"
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (
      error.response.status === 401 &&
      error.response.data.detail === "Could not validate credentials" &&
      !error.config._retry &&
      error.config.__retryCount < 3
    ) {
      error.config.__retryCount += 1;
      error.config._retry = true;
      const refresh_token = localStorage.getItem("refresh_token");
      if (refresh_token) {
        try {
          const res = await axios.post(`${BASE_URL}/users/refresh`, null, {
            headers: {
              Authorization: `Bearer ${refresh_token}`,
            },
          });
          localStorage.setItem("token", res.data.access_token);
          localStorage.setItem("refresh_token", res.data.refresh_token);
          error.config.headers["Authorization"] =
            `Bearer ${res.data.access_token}`;
          return instance.request(error.config);
        } catch (refreshError) {
          handleTokenRefreshFailure();
          return Promise.reject(refreshError);
        }
      } else {
        handleTokenRefreshFailure();
      }
    }
    return Promise.reject(error);
  }
);
export default instance;

//需要token的请求
///files/delete
///files/download/stream
///file/modifynodes
// /files/nodefiles
// /file/modifyname
// /files/img/preview
///files/video/preview
///files/download
///files/list
///users/profileimage
///files/upload
///users/delete
///users/getid
///users/files/delete
///users/upload/profileimage
