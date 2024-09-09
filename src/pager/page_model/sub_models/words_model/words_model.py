from ..base_sub_model import BaseSubModel, BaseConverter
from typing import Dict
import pytesseract
import cv2
from ..dtype import Word

import json

class WordsModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.words = []
    
    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"words": [word.to_dict() for word in self.words]}

    def read_from_file(self, path_file: str) -> None:
        self.clean_model()
        with open(path_file, "r") as f:
            phis_json = json.load(f)
       
        for word_dict in phis_json["words"]:
            word = Word(word_dict)
            self.words.append(word)
    
    def set_words_from_dict(self, word_list_dict):
        self.words = []
        for word_dict in word_list_dict:
            self.words.append(Word(word_dict))
    
    def clean_model(self):
        self.words = []

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
