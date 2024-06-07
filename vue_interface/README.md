# my-cloud-disk

## Project setup

```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### attention

配置`src/axios.js` 中的`baseURL`为你的后端接口地址。
```javascript
const instance = axios.create({
  // 基础 URL 会被添加到所有请求的 URL 前面
  baseURL: "http://localhost:8000", //替换为你的后端接口地址
  headers: {
    // 设置 Content-Type 请求头为 'application/json'
    "Content-Type": "application/json",
  },
});
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
