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


ENV JAR_PDF_PARSER=/app/models/PDF2Block/precisionPDF.jar
ENV PATH_TORCH_SEG_GNN_MODEL=/app/models/seg_gnn
ENV PATH_TORCH_SEG_LINEAR_MODEL=/app/models/seg_linear
ENV PATH_STYLE_MODEL=/app/models/style_classmodel_20250121
ENV PATH_TORCH_GLAM_NODE_MODEL=/app/models/glam_node_model_20250221
ENV PATH_TORCH_GLAM_EDGE_MODEL=/app/models/glam_edge_model_20250221
ENV PATH_TORCH_GLAM_MODEL=/app/models/glam_model_20250703
ENV PATH_TORCH_GLAM_CONF_MODEL=/app/models/glam_config_model_20250703.json
ENV PATH_TORCH_ROW_GLAM=/app/models/row_glam_20250811
ENV PATH_MODELS=/app/models
ENV DEVICE=cpu
ENV PYTHONUNBUFFERED=1


# Обновление pip
RUN python3 -m pip install --upgrade pip

WORKDIR /app
# Установка тяжелых библиотек
RUN pip install --no-cache-dir torch torch-geometric torchmetrics[detection] \
                               torchvision tokenizers transformers "huggingface_hub[cli]"

RUN huggingface-cli download google-bert/bert-base-multilingual-cased --local-dir models/bert
# Копирование проекта и установка
COPY apis apis
COPY src src
COPY models models
COPY pyproject.toml pyproject.toml
RUN python3 -m pip install .
RUN mkdir tmp_dir
# # Открытие порта и запуск приложения
CMD ["uvicorn", "apis.file2phis.app:app", "--host", "0.0.0.0", "--port", "8000"]