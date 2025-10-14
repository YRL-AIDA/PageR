from ..base_sub_model import BaseSubModel
from typing import Dict
import subprocess
import json
import os
from pdf2image import convert_from_path

from dotenv import load_dotenv
load_dotenv(override=True)

NULL_PAGE = {
    "number": -1,
    "tables": [],
    "images": [],
    "width": None,
    "height": None,
    "words": []
}

class PrecisionPDFModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.pdf_json: Dict
        self.count_page: int|None 
        # self.num_page: int = 0

    def from_dict(self, input_model_dict: Dict):
        self.pdf_json = input_model_dict

    def to_dict(self) -> Dict:
        return self.pdf_json
    

    def read_from_file(self, path_file: str, method: str = "w") -> None:
        self.path = path_file
        self.pdf_json = self.__read(path_file, method)
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def clean_model(self)-> None:
        self.pdf_json = {}
        self.count_page = None
        # self.num_page = 0
    
    def __read(self, path, method):
        jar_path = os.environ["JAR_PDF_PARSER"]
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
