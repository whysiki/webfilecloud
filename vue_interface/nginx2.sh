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

# 确保 webcloud 目录存在并复制文件
sudo mkdir -p /var/www/webcloud
sudo cp -r /root/webcloud/dist/* /var/www/webcloud/

# 配置 Nginx
sudo tee /etc/nginx/sites-available/default >/dev/null <<EOF
server {
    listen 80;
    server_name _;  # 接受所有请求，或者使用 124.70.100.14
    root /var/www/webcloud;  # 更新为新的目录
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

# 设置正确的文件权限
sudo chown -R www-data:www-data /var/www/webcloud
sudo chmod -R 755 /var/www/webcloud

# 检查 Nginx 配置
if sudo nginx -t; then
    # 重启 Nginx 服务
    sudo systemctl restart nginx
    echo "Nginx 配置已成功应用并重启。"
else
    echo "Nginx 配置测试失败，请检查配置。"
fi
