from pager.doc_model import PrecisionPDFModel, MSWordModel, PrecisionPDFToMSWord
import json
from typing import Dict
class PDF2MSWord:
    def __init__(self):
        self.precision_pdf = PrecisionPDFModel({"method": None, "page_model": None})
        self.word = MSWordModel()
        self.converter = PrecisionPDFToMSWord()

    def from_dict(self, input_model_dict: Dict):
        self.precision_pdf.from_dict(input_model_dict.copy())

    def save_doc(self, path) -> Dict:
        return self.word.save_doc(path)
    
    def extract(self) -> None:
        self.converter.convert(self.precision_pdf, self.word)

    def read_from_file(self, path_file: str) -> None:
        self.from_dict(self._read_json(path_file))

    def _read_json(self, path_file: str) -> Dict:
        with open(path_file, "r", encoding='utf-8') as f:
            json_dict = json.load(f)
        return json_dict


json2docx = PDF2MSWord()