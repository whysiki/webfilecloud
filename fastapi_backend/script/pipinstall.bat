
@REM .venv/Scripts/activate.bat
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install uvicorn
pip install fastapi
pip install argon2-cffi
pip install pyjwt
pip install loguru
pip install sqlalchemy
pip install rich
pip install python-multipart
pip install gunicorn
pip install cryptography
pip install aiofiles
pip install python-multipart
pip install requests
pip install hypercorn
pip install alembic
pip install pillow
pip install ffmpeg-python
pip install numpy
pip install imageio
pip install psycopg2-binary
pip install opencv-contrib-python

@REM sudo apt-get install ffmpeg  # 对于 Debian/Ubuntu 系统

pip freeze > requirements.txt

@REM source myenv/bin/activate
@REM python3 -m venv myenv

