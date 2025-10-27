import os
from huggingface_hub import snapshot_download

def download_model():
    current_file = os.path.realpath(__file__)
    model_dir = os.path.join(os.path.dirname(current_file), 'bert')
    snapshot_download(
        repo_id="google-bert/bert-base-multilingual-cased",
        cache_dir=model_dir,
        allow_patterns=["*.json", "*.txt", "pytorch_model.bin", "tokenizer.json"],
        etag_timeout=120,
        force_download=True
    )


if __name__ == "__main__":
    download_model()