ARG REPOSITORY="docker.io"
FROM ubuntu:22.04

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    software-properties-common \
    ffmpeg \
    libsm6 \
    libxext6 \
    openjdk-17-jre \
    && add-apt-repository -y ppa:alex-p/tesseract-ocr-devel \
    && apt-get update \
    && apt-get install -y tesseract-ocr tesseract-ocr-rus \
    && rm -rf /var/lib/apt/lists/*

# Обновление pip
RUN python3 -m pip install --upgrade pip

# Копирование проекта и установка
COPY . /app
WORKDIR /app
RUN python3 -m pip install .

# Открытие порта и запуск приложения
EXPOSE 8000
CMD ['mv', 'env_for_Docker', '.env']
CMD ["python3"]
CMD ["python3", "apis/file2phis/app.py", "--host", "0.0.0.0", "--port", "8000"]