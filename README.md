
# 项目说明

vue3 + fastapi 实现的一个前后端分离的用户隔离文件云盘项目模板. 

主要为了跨平台，跨设备，跨网络，方便的存储和管理私人文件。 界面在手机端和PC端都可以正常使用。

- [X] 用户隔离，用户头像，下载,上传, 删除, 重命名 ☑
- [x] 文件树视图，批量上传，上传到特定文件夹  ☑
- [x] 分类（文件类型），排序（大小，日期，名称），统计，查找，卡片视图，列表视图 ☑
- [x] 预览, 缩略，流式加载, gizp，并发批量删除，并发批量下载，并发批量移动，进度条 ☑
- [x] 复制直接下载链接，流链接到剪切板。 ☑ 
- [x] hls m3u8 视频流播放 ☑ 
- [x] 服务器文件存储可选对象存储或者本地存储  ☑ . （🤣）
- [x] 多部分上传和下载 🥲 (对于minio对象存储)

文件移动的实现只是修改了数据库中文件的节点路径信息，而不是真正的移动文件，所以移动文件是瞬间完成的。

文件树视图的实现是前端先通过所有文件的节点路径生成树，然后再通过树递归渲染每一层的文件夹和文件。


## 前端

[前端说明](./vue_interface/README.md)

## 后端

[后端说明](./fastapi_backend/README.md )
