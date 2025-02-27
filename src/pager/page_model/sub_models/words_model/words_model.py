from ..base_sub_model import BaseSubModel, BaseConverter
from typing import Dict
import pytesseract
import cv2
from ..dtype import Word
import numpy as np
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

class ImageToWords(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        word_list = self.extract_from_img(input_model.img)
        output_model.set_words_from_dict(word_list)


    def extract_from_img(self, img, conf={"lang": "eng+rus", "psm": 4, "oem": 3, "k": 1, "onetone_delete": False}):
        dim = (conf["k"]*img.shape[1], conf["k"]*img.shape[0])
        img_ = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        tesseract_bboxes = pytesseract.image_to_data(
            config=f"-l {conf['lang']} --psm {conf['psm']} --oem {conf['oem']}",
            image=img_,
            output_type=pytesseract.Output.DICT)
        word_list = []
        for index_bbox, level in enumerate(tesseract_bboxes["level"]):
            if level == 5:
                text = tesseract_bboxes["text"][index_bbox]
                x0 = round(tesseract_bboxes["left"][index_bbox]/conf["k"])
                y0 = round(tesseract_bboxes["top"][index_bbox]/conf["k"])
                w = round(tesseract_bboxes["width"][index_bbox]/conf["k"])
                h = round(tesseract_bboxes["height"][index_bbox]/conf["k"])
                # TODO: сделать фильтр ширины, поменять однотонный фильтер
                if conf["onetone_delete"] and np.var(img[y0:y0+h, x0:x0+w]) < 20:
                    continue
                word_list.append({
                    "text": text,
                    "x_top_left": x0,
                    "y_top_left": y0,
                    "width": w,
                    "height": h,
                })
        
        word_list = self.size_filter(word_list)
        return word_list

    def size_filter(self, word_list):
        return [word for word in word_list if word["width"] >= 2 and word["height"] >= 2]
