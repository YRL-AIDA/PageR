from abc import ABC, abstractmethod
from typing import Dict
import json

class BaseSubModel(ABC):
    @abstractmethod
    def from_dict(self, input_model_dict: Dict):
        pass

    @abstractmethod
    def to_dict(self) -> Dict:
        pass
    
    @abstractmethod
    def read_from_file(self, path_file: str) -> None:
        pass
    
    @abstractmethod
    def clean_model(self) -> None:
        pass

    def is_include_pages(self) -> bool:
        return False

    def _read_json(self, path_file: str) -> Dict:
        with open(path_file, "r", encoding='utf-8') as f:
            json_dict = json.load(f)
        return json_dict

class BaseConverter(ABC):
    @abstractmethod
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        pass



class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, model: BaseSubModel) -> None:
        pass
from typing import List

class AddArgsFromModelExtractor(BaseExtractor):
    def __init__(self, models: List[BaseSubModel]):
        self.models = models
        
    def extract(self, model: BaseSubModel) -> None:
        for m in self.models:
            new_args = list(m.__dict__.keys())
            exist_arg = list(model.__dict__.keys())
            for new_arg in new_args:
                if not (new_arg in exist_arg):
                    model.__dict__[new_arg] = m.__dict__[new_arg]

            
class BasePrinter(ABC):
    pass

class BaseLoger(ABC):
    pass


    
