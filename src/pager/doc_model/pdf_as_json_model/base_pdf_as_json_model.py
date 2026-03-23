from ..base_doc_model import BaseDocModel
from typing import Dict
from abc import ABC, abstractmethod
from ..dtype import Page, Document
from pdf2image import convert_from_path
import os 

class BaseExtractor(ABC):
    @abstractmethod
    def extract_from_path(self, path:str) -> Dict:
        pass

class BasePDFasJsonModel(BaseDocModel):
    def __init__(self, conf=None) -> None:
        self.pdf_json: Dict = {}
        self.count_page: int = 0
        self.page_model = None
        if conf and "page_model" in conf:
            self.page_model = conf["page_model"]
        self.extractor: BaseExtractor = conf["extractor"]


    @abstractmethod
    def to_dict(self) -> Dict:
        pass
    
    @property
    def document(self):
        json_dict = self.to_dict()
        pages = []
        for num_page, page_dict in enumerate(json_dict['pages']):
            page=Page(num_page)
            page.from_dict(page_dict)
            pages.append(page)
        doc = Document(pages)
        return doc
    
    def from_dict(self, input_model_dict: Dict):
        self.pdf_json = input_model_dict.copy()
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def to_dict(self) -> Dict:
        return self.pdf_json 
    

    def save_pdf_as_imgs(self, path_dir: str):
        for i, page in enumerate(self.pdf_json["pages"]):
            name_file = os.path.join(path_dir, f"page_{i}.png")
            w = int(page["width"])
            h = int(page["height"])
            img = convert_from_path(self.path, first_page=i+1, last_page=i+1, size=(w,h))[0]
            img.save(name_file)

    def read_from_file(self, path_file: str) -> None:
        self.path = path_file
        self.pdf_json = self.extractor.extract_from_path(path_file)
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def clean_model(self)-> None:
        self.pdf_json = {}
        self.count_page = None


    def extract(self) -> None:
        if not self.page_model:
            return
        for i in range(self.count_page):
            page_json = self.pdf_json["pages"][i]
            self.page_model.from_dict(page_json)
            self.page_model.extract()
            dict_page = self.page_model.to_dict()
            # TODO: удалить исходные строки и слова.
            for key in dict_page.keys():
                self.pdf_json["pages"][i][key] = dict_page[key]