#!/bin/bash

# 检查是否安装了 Nginx
if ! command -v nginx &> /dev/null
then
    echo "Nginx 未安装，正在安装..."
    sudo apt update
    sudo apt install -y nginx
    echo "Nginx 安装完成。"
else
    echo "Nginx 已经安装。"
fi

# 配置Nginx
sudo tee /etc/nginx/sites-available/default >/dev/null <<EOF
server {
    listen 80;
    server_name xxx.xxx.xxx.xxx/www.xxx.com;

    root /root/firecloud/fastapi_filecloud_backend/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
EOF

# 检查Nginx配置
sudo nginx -t

# 重启Nginx服务
sudo systemctl restart nginx



# 启动 Nginx 服务
sudo systemctl start nginx
# 重新加载 Nginx 服务
sudo systemctl reload nginx
sudo systemctl restart nginx
sudo systemctl reload nginx

echo "Nginx has been successfully configured and restarted"