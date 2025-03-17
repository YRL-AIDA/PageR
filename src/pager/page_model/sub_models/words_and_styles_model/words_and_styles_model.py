from ..base_sub_model import BaseSubModel
from typing import Dict, List
import numpy as np
from ..dtype import Word, Style



class WordsAndStylesModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.words: List[Word] = []
        self.styles: List[Style] = []
    
    def from_dict(self, input_model_dict: Dict):
        self.styles = [Style(st) for st in input_model_dict["styles"]]
        self.words = [Word(w) for w in input_model_dict["words"]]

    def to_dict(self, is_vec=False) -> Dict:
        return {"words": [word.to_dict() for word in self.words], 
                "styles": [style.to_dict(is_vec) for style in self.styles]}

    def read_from_file(self, path_file: str) -> None:
        words_and_styles_json = self._read_json(path_file)      
        for word_dict in words_and_styles_json["words"]:
            word = Word(word_dict)
            self.words.append(word)
        for style_dict in words_and_styles_json["styles"]:
            style = Style(style_dict)
            self.styles.append(style)

    def clean_model(self):
        self.words = []
        self.styles = []

    def show(self):
        print(f"count words: {len(self.words)}")
        for word in self.words:
            word.segment.plot()
        print(f"count styles: {len(self.styles)}")
        print(f"first style:")
        st = self.styles[0].to_dict(is_vec=True)
        print(np.array(st['font2vec']))
        print(f"end style:")
        st = self.styles[-1].to_dict(is_vec=True)
        print(np.array(st['font2vec']))