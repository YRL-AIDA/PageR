from ..base_sub_model import BaseSubModel
from typing import Dict
from ..dtype import Word



class WordsModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.words = []
    
    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"words": [word.to_dict() for word in self.words]}

    def read_from_file(self, path_file: str) -> None:
        phis_json = self._read_json(path_file)      
        for word_dict in phis_json["words"]:
            word = Word(word_dict)
            self.words.append(word)
    
    def set_words_from_dict(self, word_list_dict):
        self.words = []
        for word_dict in word_list_dict:
            self.words.append(Word(word_dict))
    
    def clean_model(self):
        self.words = []

