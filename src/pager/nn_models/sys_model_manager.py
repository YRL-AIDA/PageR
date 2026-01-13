from pathlib import Path
import shutil
import os

models = {
    # "precisionPDF.jar": Path("models/PDF2Block/precisionPDF.jar"),
    "precisionPDF.jar": Path("models/PDF2Block/precision_pdf_pager.jar"),
    "rows2regions-GLAM": Path("models/Rows2Regions/row2region_GLAM_20260113"),
    "words2rows-GLAM": Path("models/Words2Rows/words2rows_glam_20251113"),
    "style_classmodel": Path("models/Words2Rows/style_classmodel_20250121"),
}

def get_model_path(model_name: str) -> Path:
    cache_dir = get_cache_dir()/model_name
    return cache_dir

def download_models():
    """Запись моделей в .cache/pager"""
    cache_dir = get_cache_dir()
    os.makedirs(cache_dir, exist_ok=True)

    # Копируем модели в кэш
    for model_name, local_path in models.items():
        model_path = cache_dir / model_name
        # if not model_path.exists():
        print(local_path)
        if not local_path.exists():
            continue
        shutil.copy2(local_path, model_path)
        
        print(f"Downloaded {model_name} to {model_path}")
    
    # Скачивание моделей в кэш 
    bert_cache_dir = cache_dir/'bert'
    if not bert_cache_dir.exists():
        print("INSTALL BERT")
        from transformers import BertTokenizer, BertModel
        model_name = 'bert-base-multilingual-cased'
        model_dir = os.path.join(bert_cache_dir, 'models--bert-base-multilingual-cased',
                                'snapshots','3f076fdb1ab68d5b2880cb87a0886f315b8146f8')
        # try:
        tokenizer = BertTokenizer.from_pretrained(model_name, cache_dir=bert_cache_dir)
        model = BertModel.from_pretrained(model_name, cache_dir=bert_cache_dir).to('cpu')
        # except:
        #     tokenizer = BertTokenizer.from_pretrained(model_dir)
        #     model = BertModel.from_pretrained(model_dir).to('cpu')
            
            
            

def get_cache_dir() -> Path:
    """Возвращает путь к кэш-директории"""
    home = Path.home()
    cache_dir = home / ".cache" / "pager"
    return cache_dir

if __name__ == "__main__":
    download_models()