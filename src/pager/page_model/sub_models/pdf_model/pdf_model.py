from ..base_sub_model import BaseSubModel
from typing import Dict
import subprocess
import json
import os


class PDFModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.json: Dict
        self.count_page: int
        self.num_page: int = 0

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return self.json["pages"][self.num_page]

    def read_from_file(self, path_file: str) -> None:
        self.json = self.__read(path_file)
        self.count_page = len(self.json['pages'])
    
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
    
    def __read(self, path):
        jar_path = os.environ["JAR_PDF_PARSER"]
        res = subprocess.run(["java", "-jar", jar_path, "-i", path, "-w"], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        if res.stderr:
            print(res.stderr.decode("utf-8"))
        return json.loads(res.stdout.decode("utf-8"))

class NotThisNumberPage(Exception):
    def __init__(self, num):
        self.num = num
    def __str__(self) -> str:
        return f'Not this {self.num} page'
