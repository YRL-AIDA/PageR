from ..base_sub_model import BaseSubModel, BaseConverter
from typing import Dict, List
import pytesseract
import cv2
from ..dtype import Style, StyleWord, ImageSegment
from ..words_model import ImageToWords
import json
import numpy as np

from .model_scripts.model_20250121 import classifier_image_word, get_model

class WordsAndStylesModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.words: List[StyleWord] = []
        self.styles: List[Style] = []
    
    def from_dict(self, input_model_dict: Dict):
        self.styles = [Style(st) for st in input_model_dict["styles"]]
        self.words = [StyleWord(w) for w in input_model_dict["words"]]

    def to_dict(self, is_vec=False) -> Dict:
        return {"words": [word.to_dict() for word in self.words], 
                "styles": [style.to_dict(is_vec) for style in self.styles]}

    def read_from_file(self, path_file: str) -> None:
        words_and_styles_json = self._read_json(path_file)      
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
                "size": word["font_size"],
                "font_type": word["font_type"],
                "italic": word["italic"],
                "width": 1.0 if word["bold"] else 0.0
            }
            
            index_style = self._get_style(tmp_style, styles)           
            if index_style == -1:
                styles.append(tmp_style)
                index_style = len(styles) - 1 
            words.append({"style_id": index_style,
                          "content": word["text"],
                          "segment": word,
                          "type_align": None})
        for i, style in enumerate(styles):
            style["id"] = i
        return [StyleWord(word) for word in words], [Style(style) for style in styles]


    def _get_style(self, style, styles):
        for i, style_ in enumerate(styles):
            if style_ == style:
                return i
        return -1


class ImageToWordsAndStyles(BaseConverter):
    def __init__(self, conf=None):
        self.conf = {"lang": "eng+rus", "psm": 4, "oem": 3, "k": 1}
        if conf is not None:
            for key, value in conf.items():
                if key in self.conf.items():
                    self.conf[key] = value


    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        conv_image_to_words = ImageToWords()
        word_list = conv_image_to_words.extract_from_img(input_model.img, conf=self.conf)
        word_list, style_list = self.separate(word_list, input_model.img)
        output_model.words = word_list
        output_model.styles = style_list

    def separate(self, words_json, img):
        styles = []
        words = []
        for word in words_json:
            
            seg = ImageSegment(dict_p_size=word)
            word_img = cv2.cvtColor(seg.get_segment_from_img(img), cv2.COLOR_RGB2GRAY)/255
            

            tmp_style = {       
                "font2vec": self.get_style_from_word_img(word_img)
            }
            index_style = self._get_style(tmp_style, styles, delta_ = 0.1)           
            if index_style == -1:
                styles.append(tmp_style)
                index_style = len(styles) - 1 
            words.append({"style_id": index_style,
                          "content": word["text"],
                          "segment": word,
                          "type_align": None})
        for i, style in enumerate(styles):
            style["id"] = i
        return [StyleWord(word) for word in words], [Style(style) for style in styles]


    def _get_style(self, style, styles, delta_):
        for i, style_ in enumerate(styles):
            x1 = np.array(style_["font2vec"])
            x2 = np.array(style["font2vec"])
            if np.dot(x1-x2, x1-x2) < delta_:
                return i
        return -1

    def get_style_from_word_img(self, word_img):
        horizon = np.mean(word_img, axis=0)
        vertical = np.mean(word_img, axis=1)
        diff_vertical = np.diff(vertical)
        h = word_img.shape[0]
        vec_style = [
            np.min(horizon),
            np.max(horizon),
            np.mean(horizon),
            np.std(horizon),
            np.mean(vertical),
            np.argmax(diff_vertical)/h,
            np.argmin(diff_vertical)/h
        ]
        return vec_style
    
class ImageToWordsAndCNNStyles(ImageToWordsAndStyles):
    def __init__(self, conf=None):
        super().__init__(conf)
        self.model = get_model(conf["path_model"])
    
    def get_style_from_word_img(self, word_img):
        return classifier_image_word(self.model, word_img).detach().numpy()