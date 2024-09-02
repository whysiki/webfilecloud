# #!/bin/bash

# # 安装 Nginx
# # sudo apt update
# # sudo apt install -y nginx

# # 创建 Nginx 配置文件
# NGINX_CONF="/etc/nginx/sites-available/filecloud"
# sudo tee $NGINX_CONF > /dev/null <<EOL
# server {
#     listen 80;
#     server_name 8.138.124.53;

# root /root/firecloud/fastapi_filecloud_backend/dist;
# index index.html;


#     location /filecloud {
#         try_files $uri $uri/ /index.html;
#     }
# }
# EOL

# # 创建符号链接以启用配置
# sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/

# # 启动 Nginx 服务
# sudo systemctl start nginx

# # 测试 Nginx 配置
# sudo nginx -t

# # 重新加载 Nginx 服务
# sudo systemctl reload nginx
# sudo systemctl restart nginx
# sudo systemctl reload nginx
# # 检查 Nginx 服务状态
# # sudo systemctl status nginx
# # 日志文件
# # sudo cat /var/log/nginx/error.log