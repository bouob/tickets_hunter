# 使用具有 Node.js 的官方 Python 基礎映像
FROM python:3.10-slim-buster

# 安裝 Node.js
RUN apt-get update && apt-get install -y nodejs npm

# 升級 pip
RUN python3 -m pip install --upgrade pip

# 安裝 Python 和 Node.js 套件
COPY requirements.txt ./
COPY package.json ./
RUN pip install -r requirements.txt
RUN npm install

# 安裝 Chrome 瀏覽器和 ChromeDriver 以供 Selenium 使用
RUN apt-get update && apt-get install -y wget gnupg2 unzip
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
RUN wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN mv chromedriver /usr/bin/chromedriver
RUN chown root:root /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver

# 設定工作目錄
WORKDIR /app

# 複製應用程式程式碼到 Docker 容器
COPY . .

# 預設命令
CMD ["python3", "setting.py"]