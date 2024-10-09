from .sub_models.base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from typing import Dict, List


class PageModelUnit:
    def __init__(self, id:str, sub_model: BaseSubModel, extractors: List[BaseExtractor], converters: Dict[str, BaseConverter]) -> None:
        self.id = id
        self.sub_model = sub_model
        self.extractors = extractors
        self.converters = converters
    
    def from_dict(self, input_dict: Dict):
        self.sub_model.from_dict(input_dict)

    def read_from_file(self, path:str):
        self.sub_model.read_from_file(path)

    def to_dict(self):
        return self.sub_model.to_dict()


class PageModel:
    def __init__(self, page_units: List[PageModelUnit]) -> None:
        self.page_units = page_units
        self.keys = {}
        for i, page_unit in enumerate(page_units):
            self.keys[page_unit.id] = i
    
    def next_page(self) -> None:
        if not page_units[0].sub_model.is_include_pages():
            raise ModelNotIncludePage()
        page_units[0].sub_model.next() 

    def back_page(self) -> None:
        if not page_units[0].sub_model.is_include_pages():
            raise ModelNotIncludePage()
        page_units[0].sub_model.back() 
            

    def read_from_file(self, path) -> None:
        self.page_units[0].read_from_file(path)
    
    def extract(self):
        for page_unit in self.page_units:
            for id_model, conv in page_unit.converters.items():
                conv.convert(self.page_units[self.keys[id_model]].sub_model, page_unit.sub_model)
            
            for extr in page_unit.extractors:
                extr.extract(page_unit.sub_model)
    
    def from_dict(self, input_dict: Dict, id_model:str = None) -> None:
        if id_model is None:
            self.page_units[0].from_dict(input_dict)
            return
        self.page_units[self.keys[id_model]].from_dict(input_dict)

    def to_dict(self, id_model:str = None) -> Dict:
        if id_model is None:
            return self.page_units[-1].to_dict()
        return self.page_units[self.keys[id_model]].to_dict()
        
class ModelNotIncludePage(Exception):
    def __str__(self):
        return f"Model is not include page"
 
