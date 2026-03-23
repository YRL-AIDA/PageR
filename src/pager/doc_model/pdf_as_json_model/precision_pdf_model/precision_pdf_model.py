from typing import Dict
import subprocess
import json
import os

from pager.nn_models.sys_model_manager import get_model_path
from .exaption_pdf import MethodConflict, NotMethodParsing
from pager.page_model import PageModel
from ..base_pdf_as_json_model import BasePDFasJsonModel, BaseExtractor


class JarExtractor(BaseExtractor):
    def __init__(self, conf=None) -> None:
        if "jar_path" in conf.keys():
            self.jar_path = conf["jar_path"]
        else:
            self.jar_path = get_model_path("precisionPDF.jar")

    def extract_from_path(self, path):
        
        comands =["java", "-jar", self.jar_path, "-i", path]
        
        res = subprocess.run(comands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.stderr:
            print(res.stderr.decode("utf-8"))
        try:
            str_ = res.stdout.decode("utf-8", errors="replace")
            json_ = json.loads(str_)
            return json_
        except json.JSONDecodeError as e:
            print(e, "<stdout = ", str_, ">")
            return dict()


class PrecisionPDFModel(BasePDFasJsonModel):
    def __init__(self, conf=None) -> None:
        if conf is None:
            conf = {}
        conf['extractor'] = JarExtractor(conf)
        super().__init__(conf)
        
        





    
    
    


