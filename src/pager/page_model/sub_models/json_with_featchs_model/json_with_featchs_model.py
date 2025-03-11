from ..base_sub_model import BaseSubModel
from typing import Dict, List, Callable, Any
import numpy as np
import matplotlib.pyplot as plt
import json

class JsonWithFeatchs(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        #json - хранит результат, без перезаписи
        self.json = {}

    def add_featchs(self, fun_update: Callable[[], List[Any]], names: List[str], is_reupdate: bool = False, rewrite=False) -> None:
        # TODO: только одно свойство меняется

        # Проверка, что все содержатся 
        is_contain_all = True
        for name in names:
            if not self.contains(name):
                is_contain_all = False
        if is_contain_all and not is_reupdate:
            return
        
        rez = fun_update()
        if len(rez) != len(names):
            raise Exception('len(rez) != len(names)')
        
        for name_featch, val_featch in zip(names, rez):
            self.__dict__[name_featch] = val_featch
            self.update_json(name_featch, is_reupdate)
        if rewrite:
            with open(self.__name_json_file, 'w') as f:
                json.dump(self.to_dict(), f)

    def contains(self, name: str) -> bool:
        return name in self.json.keys()

    def from_dict(self, input_model_dict: Dict):
        self.json = input_model_dict

    def to_dict(self, all: bool = False) -> Dict:
        if all:
            _json = self.json.copy()
            for name, val in self.__dict__.items():
                if not name in self.json.keys() and name!='json':
                    _json[name] = val
            return _json
        
        return self.json
    
    def update_json(self, name: str, is_reupdate: bool = False) -> None:
        if not name in self.json.keys() or is_reupdate:
            self.json[name] = self.__dict__[name]
    
    def read_from_file(self, path_file: str) -> None:
        self.clean_model()
        self.json = self._read_json(path_file)
        self.__name_json_file = path_file

    def clean_model(self):
        self.__dict__ = {}
        self.json = {}

    def show(self):
        for key, value in self.json.items():
            if type(value) == list:
                count_ = len(value)
                str_ = f'{key} : {value[0]} ... {value[-1]} ({count_})' if count_ > 0 else f'{key} : None'
                print(str_ )
            elif type(value) == dict:
                print(f'{key} : {",".join(value.keys())}')
            else:
                print(f'{key} : {value}')