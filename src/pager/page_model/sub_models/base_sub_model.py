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

class BasePrinter(ABC):
    pass

class BaseLoger(ABC):
    pass


    
