from ..base_sub_model import BaseSubModel, BaseConverter
from typing import Dict, List
import pytesseract
import cv2
from ..dtype import Style, StyleWord

import json

class WordsAndStylesModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.words: List[StyleWord] = []
        self.styles: List[Style] = []
    
    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"words": [word.to_dict() for word in self.words], 
                "styles": [style.to_dict() for style in self.styles]}

    def read_from_file(self, path_file: str) -> None:
        self.clean_model()
        with open(path_file, "r") as f:
            words_and_styles_json = json.load(f)
       
        for word_dict in words_and_styles_json["words"]:
            word = StyleWord(word_dict)
            self.words.append(word)
        for style_dict in words_and_styles_json["styles"]:
            style = Style(style_dict)
            self.styles.append(style)

    def clean_model(self):
        self.words = []
        self.styles = []


class PdfToWordsAndStyles(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        page_json = input_model.to_dict()
        word_list, style_list = self.separate(page_json['words'])
        output_model.words = word_list
        output_model.styles = style_list

    def separate(self, words_json):
        styles = []
        words = []
        for word in words_json:
            tmp_style = {       
                "type": word['type'],
                "font_size": word["font_size"]
            }
            index_style = self._get_style(tmp_style, styles)           
            if index_style == -1:
                styles.append(tmp_style)
                index_style = len(styles) - 1 
            words.append({"style_id": index_style,
                          "content": word["text"],
                          "y": word["y_top_left"] + word["height"],
                          "x": word["x_top_left"],
                          "type_align": None})
        for i, style in enumerate(styles):
            style["id"] = i
        return [StyleWord(word) for word in words], [Style(style) for style in styles]


    def _get_style(self, style, styles):
        for i, style_ in enumerate(styles):
            if style_ == style:
                return i
        return -1
