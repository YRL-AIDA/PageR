from typing import Dict
import subprocess
import json
import os
from pdf2image import convert_from_path
from pager.nn_models.sys_model_manager import get_model_path
from .exaption_pdf import MethodConflict, NotMethodParsing
from pager.page_model import PageModel

NULL_PAGE = {
    "number": -1,
    "tables": [],
    "images": [],
    "width": None,
    "height": None,
    "words": []
}

class ImageAsPrecisionPDFModel():
    def __init__(self, conf=None) -> None:
        page_0 = NULL_PAGE.copy()
        page_0["number"] = 0
        self.pdf_json = {"pages": [page_0]}
        self.count_page: int|None = 1
        self.page_model: PageModel = conf["page_model"]

    def from_dict(self, input_model_dict: Dict):
        self.pdf_json = input_model_dict.copy()

    def to_dict(self) -> Dict:
        return self.pdf_json
    
    def extract(self) -> None:
        for i in range(self.count_page):
            page_json = self.pdf_json["pages"][i]
            self.page_model.from_dict(page_json)
            self.page_model.extract()
            h, w = self.page_model.page_units[0].sub_model.img.shape[:2]
            dict_page = self.page_model.to_dict()
            dict_page["width"], dict_page["height"] = w, h
            # TODO: удалить исходные строки и слова.
            for key in dict_page.keys():
                self.pdf_json["pages"][i][key] = dict_page[key]


    def read_from_file(self, path_file: str) -> None:
        self.page_model.read_from_file(path_file)

    def clean_model(self)-> None:
        page_0 = NULL_PAGE.copy()
        page_0["number"] = 0
        self.pdf_json = {"pages": [page_0]}
        self.count_page = 1
