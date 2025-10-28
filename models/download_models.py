import os
from transformers import BertTokenizer, BertModel

def download_model():
    model_name = "bert-base-multilingual-cased"
    current_file = os.path.realpath(__file__)
    cache_dir = os.path.join(os.path.dirname(current_file), 'bert')
    model_dir = os.path.join(cache_dir, 'models--bert-base-multilingual-cased',
                             'snapshots','3f076fdb1ab68d5b2880cb87a0886f315b8146f8')
    print(model_dir)
    try:
        tokenizer = BertTokenizer.from_pretrained(model_dir)
        model = BertModel.from_pretrained(model_dir).to('cpu')
    except:
        tokenizer = BertTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = BertModel.from_pretrained(model_name, cache_dir=cache_dir).to('cpu')
    inputs = tokenizer(['test', 'BERT'], return_tensors="pt", padding=True).to('cpu')
    outputs = model(**inputs)
    print(outputs)

if __name__ == "__main__":
    download_model()