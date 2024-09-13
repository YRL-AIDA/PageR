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
"""
class ImageToWords(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        word_list = self.extract_from_img(input_model.img)
        output_model.set_words_from_dict(word_list)


    def extract_from_img(self, img, conf={"lang": "eng+rus", "psm": 4, "oem": 3, "k": 1}):
        dim = (conf["k"]*img.shape[1], conf["k"]*img.shape[0])
        img_ = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        tesseract_bboxes = pytesseract.image_to_data(
            config=f"-l {conf['lang']} --psm {conf['psm']} --oem {conf['oem']}",
            image=img_,
            output_type=pytesseract.Output.DICT)
        word_list = []
        for index_bbox, level in enumerate(tesseract_bboxes["level"]):
            if level == 5:
                word_list.append({
                    "text": tesseract_bboxes["text"][index_bbox],
                    "x_top_left": round(tesseract_bboxes["left"][index_bbox]/conf["k"]),
                    "y_top_left": round(tesseract_bboxes["top"][index_bbox]/conf["k"]),
                    "width": round(tesseract_bboxes["width"][index_bbox]/conf["k"]),
                    "height": round(tesseract_bboxes["height"][index_bbox]/conf["k"]),
                })
        return word_list
"""
