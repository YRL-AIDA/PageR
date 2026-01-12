from ..base_sub_model import BaseConverter
from ..image_model import ImageModel
from ..words_model import WordsModel
import re
import pytesseract
import cv2
import numpy as np

class Image2Words(BaseConverter):
    def __init__(self, conf=None):
        self.conf = {"lang": "eng+rus", "psm": 4, "oem": 3, "k": 1, "onetone_delete": False}
        if conf is None:
            return
        for key, val in conf.items():
            if key in self.conf.keys():
                self.conf[key] = val

    def convert(self, input_model: ImageModel, output_model: WordsModel)-> None:
        word_list = self.extract_from_img(input_model.img)
        words = []
        others = []
        for w in word_list:
            if re.match(r'^\s*$', w["text"]):
                others.append(w)
            else:
                words.append(w)
        output_model.set_words_from_dict(words)
        output_model.set_others_from_dict(others)


    def extract_from_img(self, img):
        conf = self.conf
        dim = (conf["k"]*img.shape[1], conf["k"]*img.shape[0])
        if conf["k"] == 1:
            img_ = img
        elif conf["k"] < 1:
            img_ = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        else:
            img_ = cv2.resize(img, dim, interpolation = cv2.INTER_NEAREST)
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
