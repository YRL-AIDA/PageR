from pager.doc_model import MSWordModel
from pager.doc_model import PrecisionPDFModel, PrecisionPDFToMSWord
from pager.doc_model import MinerPDFModel, MinerPDFToMSWord
import json
from typing import Dict
class PDF2MSWord:
    def __init__(self):
        # self.pdf_reader = PrecisionPDFModel({"method": None, "page_model": None})
        self.pdf_reader = MinerPDFModel()
        self.word = MSWordModel()
        # self.converter = PrecisionPDFToMSWord()
        self.converter = MinerPDFToMSWord()

    def from_dict(self, input_model_dict: Dict):
        self.pdf_reader.from_dict(input_model_dict.copy())

    def save_doc(self, path) -> Dict:
        return self.word.save_doc(path)
    
    def extract(self) -> None:
        self.converter.convert(self.pdf_reader, self.word)

    def read_from_file(self, path_file: str) -> None:
        self.from_dict(self._read_json(path_file))

    def _read_json(self, path_file: str) -> Dict:
        with open(path_file, "r", encoding='utf-8') as f:
            json_dict = json.load(f)
        return json_dict


json2docx = PDF2MSWord()