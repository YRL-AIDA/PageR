from ..base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from typing import Dict, List
import docx


class MSWordModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.doc: docx.Document
        
    
    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        pass
        # return {"blocks": [block.to_dict() for block in self.blocks]}

    def read_from_file(self, path_file: str) -> None:
        self.doc = docx.Document(path_file)

    def clean_model(self):
        self.doc = None