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
    poppler-utils \
    openjdk-17-jre \
    && add-apt-repository -y ppa:alex-p/tesseract-ocr-devel \
    && apt-get update \
    && apt-get install -y tesseract-ocr tesseract-ocr-rus \
    && rm -rf /var/lib/apt/lists/* 

# Обновление pip
RUN python3 -m pip install --upgrade pip

WORKDIR /app
# Установка тяжелых библиотек
RUN pip install --no-cache-dir torch torch-geometric torchmetrics[detection] \
                               torchvision tokenizers transformers 
ENV PYTHONUNBUFFERED=1

# RUN huggingface-cli download google-bert/bert-base-multilingual-cased --local-dir models/bert
# Копирование проекта и установка
COPY apis apis
COPY src src
COPY models models
COPY pyproject.toml pyproject.toml
RUN python3 -m pip install .
COPY models/bert /.cache/pager/bert
RUN pager-install-models
RUN mkdir tmp_dir
# # Открытие порта и запуск приложения
CMD ["uvicorn", "apis.file2phis.app:app", "--host", "0.0.0.0", "--port", "8000"]