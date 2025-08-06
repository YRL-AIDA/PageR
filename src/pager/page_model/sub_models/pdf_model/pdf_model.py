from ..base_sub_model import BaseSubModel
from typing import Dict

from .precision_pdf_model import PrecisionPDFModel

NULL_PAGE = {
    "number": -1,
    "tables": [],
    "images": [],
    "width": None,
    "height": None,
    "words": []
}

class PDFModel(BaseSubModel):
    def __init__(self, conf=None) -> None:
        super().__init__()
        self.pdf_json: Dict
        self.count_page: int
        self.num_page: int = 0
        self.pdf_parser = PrecisionPDFModel()
        if conf and "method" in conf.keys():
            self.method = conf["method"]


    def from_dict(self, input_model_dict):
        pass
    
    def to_dict(self) -> Dict:
        return self.pdf_json["pages"][self.num_page] if "pages" in self.pdf_json.keys() else NULL_PAGE

    def read_from_file(self, path_file: str, method=None) -> None:
        self.path = path_file
        self.pdf_parser.read_from_file(path_file, method=method if method else self.method)
        self.pdf_json = self.pdf_parser.to_dict()
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def clean_model(self)-> None:
        self.pdf_json = {}
        self.count_page = None
        self.num_page = 0
    
    def is_include_pages(self) -> bool:
        return True
   
    def is_final_page(self) -> bool:
        return self.num_page == self.count_page - 1
    
    def is_start_page(self) -> bool:
        return self.num_page == 0

    def next_page(self) -> None:
        if self.is_final_page():
            raise NotThisNumberPage(self.num_page + 1)
        self.num_page += 1
    
    def back_page(self) -> None:
        if self.is_start_page():
            raise NotThisNumberPage(self.num_page - 1)
        self.num_page -= 1


class NotThisNumberPage(Exception):
    def __init__(self, num):
        self.num = num
    def __str__(self) -> str:
        return f'Not this {self.num} page'
