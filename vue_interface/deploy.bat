@REM dist 
@REM 8.138.124.53
@REM /root/firecloud/fastapi_filecloud_backend/dist

@REM npm run build && scp -r dist root@8.138.124.53:/root/firecloud/fastapi_filecloud_backend/ && ssh root@8.138.124.53 'bash /root/firecloud/fastapi_filecloud_backend/nginx2.sh'

@REM ssh root@8.138.124.53 'bash /root/firecloud/fastapi_filecloud_backend/nginx2.sh'

@REM chmod +x /root/firecloud/fastapi_filecloud_backend/nginx1.sh

@REM echo "778899vvbbnnmmC" | sshpass scp -r dist root@8.138.124.53:/root/firecloud/fastapi_filecloud_backend/ && sshpass -p "778899vvbbnnmmC" ssh root@8.138.124.53 'bash /root/firecloud/fastapi_filecloud_backend/nginx1.sh'

@REM sudo rm /etc/nginx/sites-available/filecloud
@REM sudo rm /etc/nginx/sites-enabled/filecloud
@REM sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
@REM sudo systemctl reload nginx


@REM  ssh-keygen -t rsa
@REM Generating public/private rsa key pair.
@REM Enter file in which to save the key (C:\Users\Administrator/.ssh/id_rsa):
@REM Enter passphrase (empty for no passphrase): 
@REM Enter same passphrase again: 
@REM Your identification has been saved in C:\Users\Administrator/.ssh/id_rsa
@REM Your public key has been saved in C:\Users\Administrator/.ssh/id_rsa.pub
@REM The key fingerprint is:
@REM SHA256:3sHZTxlTbAEcCkrx1KJ5WrluvzenpVyyYMln5/Ck0m8 administrator@S
@REM The key's randomart image is:
@REM +---[RSA 3072]----+
@REM |       o.o. .oooo|
@REM |      . +..... .o|
@REM |       .o.o.  o. |
@REM |       o = o   + |
@REM |        S = . o  |
@REM |       o o...o   |
@REM |        o .=.=.= |
@REM |         o..=+&E |
@REM |        . .o+**+ |
@REM +----[SHA256]-----+
@REM notepad C:\Users\Administrator/.ssh/id_rsa.pub
@REM cat ~/.ssh/id_rsa.pub | ssh root@8.138.124.53 'cat >> ~/.ssh/authorized_keys'
@REM ssh root@8.138.124.53
@REM sudo nano ~/.ssh/authorized_keys
@REM chmod 600 ~/.ssh/authorized_keys
@REM sudo nano /etc/ssh/sshd_config PubkeyAuthentication yes
@REM sudo systemctl restart ssh
@REM ~/.ssh/authorized_keys

@REM cat ~/.ssh/id_rsa.pub | ssh root@8.138.124.53 'mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'

@REM Get-Content ~/.ssh/id_rsa.pub


@REM > /root/.ssh/authorized_keys

@REM chmod 700 ~/.ssh
@REM chmod 600 ~/.ssh/authorized_keys

