from ..base_sub_model import BaseSubModel
from typing import Dict
import subprocess
import json
import os


class PDFModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.json: Dict

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return self.json

    def read_from_file(self, path_file: str) -> None:
        self.json = self.__read(path_file)


    def __read(self, path):
        jar_path = os.environ["JAR_PDF_PARSER"]
        res = subprocess.run(["java", "-jar", jar_path, "-i", path], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.stderr:
            print(res.stderr.decode("utf-8"))
        return json.loads(res.stdout.decode("utf-8"))

    
