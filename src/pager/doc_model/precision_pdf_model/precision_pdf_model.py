from typing import Dict
import subprocess
import json
import os
from pdf2image import convert_from_path
from pager.nn_models.sys_model_manager import get_model_path
from .exaption_pdf import MethodConflict, NotMethodParsing
from pager.page_model import PageModel

class PrecisionPDFModel():
    def __init__(self, conf=None) -> None:
        self.pdf_json: Dict
        self.count_page: int|None 
        self.method = conf["method"] if conf and "method" in conf.keys() else None
        self.page_model: PageModel = conf["page_model"]

    def from_dict(self, input_model_dict: Dict):
        self.pdf_json = input_model_dict.copy()
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def to_dict(self) -> Dict:
        return self.pdf_json 
    
    def extract(self) -> None:
        for i in range(self.count_page):
            page_json = self.pdf_json["pages"][i]
            self.page_model.from_dict(page_json)
            self.page_model.extract()
            dict_page = self.page_model.to_dict()
            # TODO: удалить исходные строки и слова.
            for key in dict_page.keys():
                self.pdf_json["pages"][i][key] = dict_page[key]


    def read_from_file(self, path_file: str, method: str| None = None) -> None:
        if method and self.method:
            if method != self.method:
                raise MethodConflict(self.method, method)

        if not method:
            if not self.method:
                raise NotMethodParsing()
            else:
                method = self.method
        
        self.path = path_file
        self.pdf_json = self.__read(path_file, method)
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def clean_model(self)-> None:
        self.pdf_json = {}
        self.count_page = None
    
    def __read(self, path, method):
        jar_path = get_model_path("precisionPDF.jar")
        comands =["java", "-jar", jar_path, "-i", path]
        if method == "w":
            comands.append("-w")
        elif method != "r":
            raise ValueError('Methon "r" - rows or  "w" - words')

        
        res = subprocess.run(comands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.stderr:
            print(res.stderr.decode("utf-8"))
        try:
            str_ = res.stdout.decode("utf-8")
            json_ = json.loads(str_)
            return json_
        except json.JSONDecodeError as e:
            print(e, "<stdout = ", str_, ">")
            return dict()

    def save_pdf_as_imgs(self, path_dir: str):
        for i, page in enumerate(self.pdf_json["pages"]):
            name_file = os.path.join(path_dir, f"page_{i}.png")
            w = int(page["width"])
            h = int(page["height"])
            img = convert_from_path(self.path, first_page=i+1, last_page=i+1, size=(w,h))[0]
            img.save(name_file)
