from ..base_sub_model import BaseSubModel
from typing import Dict

NULL_PAGE = {
    "number": -1,
    "tables": [],
    "images": [],
    "width": None,
    "height": None,
    "rows": []
}

class PDFModel(BaseSubModel):
    """
    PrecisionPDF - json модель, которая работает со страницами
    """
    def __init__(self, conf=None) -> None:
        super().__init__()
        self.page_pdf_json: Dict

    def from_dict(self, input_model_dict):
        self.page_pdf_json = input_model_dict
    
    def to_dict(self) -> Dict:
        return self.page_pdf_json

    def read_from_file(self, path_file: str) -> None:
        self.from_dict(self._read_json(path_file))

       
    def clean_model(self)-> None:
        self.page_pdf_json = {}


