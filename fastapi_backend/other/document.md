<!-- ## 用户管理

### 注册用户

- **URL**: `/users/register`
- **Method**: `POST`
- **Data Params**: 
  ```json
  {
    "username": "[string]", // 用户名长度至少为 3 位
    "password": "[string]" // 密码长度至少为 8 位
  }
  ```
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "username": "[string]",
      "message": "User created successfully",
      "id": "[string]"
    }
    ```

### 用户登录

- **URL**: `/users/login`
- **Method**: `POST`
- **Data Params**: 
  ```json
  {
    "username": "[string]",
    "password": "[string]"
  }
  ```
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "access_token": "[string]",
      "token_type": "bearer"
    }
    ```

### 删除用户

- **URL**: `/users/delete`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer [access_token]`
- **URL Params**: `id=[string]` // 用户 ID
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "id": "[string]",
      "username": "[string]",
      "message": "User deleted successfully."
    }
    ```

### 获取当前用户信息

- **URL**: `/users/me`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer [access_token]`
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "message": "info of current user",
      "id": "[string]",
      "username": "[string]",
      "register_time": "[datetime]",
      "files": "[string]"
    }
    ```

## 文件管理

### 上传文件

- **URL**: `/files/upload`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer [access_token]`
- **Data Params**: `file: [binary]`
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "id": "[string]",
      "filename": "[string]",
      "file_size": "[string]",
      "message": "Upload file successful",
      "file_create_time": "[datetime]",
      "file_type": "[string]",
      "file_owner_name": "[string]"
    }
    ```

### 下载文件

- **URL**: `/files/download`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer [access_token]`
- **URL Params**: `file_id=[string]` // 文件 ID
- **Success Response**: 
  - **Code**: `200`
  - **Content**: `binary`

### 列出用户的所有文件

- **URL**: `/files/list`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer [access_token]`
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "files": [
        {
          "id": "[string]",
          "filename": "[string]",
          "file_size": "[string]",
          "message": "File found",
          "file_create_time": "[datetime]",
          "file_type": "[string]",
          "file_owner_name": "[string]"
        },
        ...
      ]
    }
    ```

### 删除文件

- **URL**: `/files/delete`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer [access_token]`
- **URL Params**: `file_id=[string]` // 文件 ID
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "message": "File deleted successfully",
      "id": "[string]",
      "filename": "[string]",
      "file_size": "[string]",
      "file_create_time": "[datetime]",
      "file_type": "[string]",
      "file_owner_name": "[string]"
    }
    ```

### 获取文件信息

- **URL**: `/files/info`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer [access_token]`
- **URL Params**: `file_id=[string]`
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "id": "[string]",
      "filename": "[string]",
      "file_size": "[string]",
      "message": "File found",
      "file_create_time": "[datetime]",
      "file_type": "[string]",
      "file_owner_name": "[string]",
      "file_path": "[string]"
    }
    ```

<!-- ## 数据库管理

### 重置数据库 (仅管理员可用) 同时会删除所有文件

- **URL**: `/db/reset`
- **Method**: `POST`
- **Data Params**: 
  ```json
  {
    "username": "[string]", // 管理员用户名
    "password": "[string]" // 管理员密码
  }
  ```
- **Success Response**: 
  - **Code**: `200`
  - **Content**: 
    ```json
    {
      "message": "Database reset successfully and all files deleted.",
      "user_count": "[integer]",
      "file_count": "[integer]"
    }
    ``` --> -->