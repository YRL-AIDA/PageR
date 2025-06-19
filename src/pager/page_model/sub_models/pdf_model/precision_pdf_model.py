from ..base_sub_model import BaseSubModel
from typing import Dict
import subprocess
import json
import os
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
        # self.count_page: int
        # self.num_page: int = 0

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return self.pdf_json
    

    def read_from_file(self, path_file: str, method: str = "w") -> None:
        self.path = path_file
        self.pdf_json = self.__read(path_file, method)
        self.count_page = len(self.pdf_json['pages']) if "pages" in self.pdf_json.keys() else 0

    def clean_model(self)-> None:
        self.pdf_json = {}
        # self.count_page = None
        # self.num_page = 0
    
    def __read(self, path, method):
        jar_path = os.environ["JAR_PDF_PARSER"]
        comands =["java", "-jar", jar_path, "-i", path]
        if method == "w":
            comands.append("-w")
        
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
