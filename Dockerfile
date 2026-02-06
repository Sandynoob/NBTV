# 使用官方提供的穩定映像檔，內含 Chrome 和驅動
FROM selenium/standalone-chrome:latest

# 切換到 root 使用者來安裝 Python 環境和 pip
USER root

# 安裝 Python3 和 pip
RUN apt-get update && apt-get install -y python3 python3-pip --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 將本地文件複製到容器
COPY . .

# 安裝 selenium 庫
RUN pip3 install selenium

# 容器啟動時運行 main.py
CMD ["python3", "main.py"]
