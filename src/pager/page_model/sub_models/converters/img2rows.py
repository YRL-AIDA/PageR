from ..base_sub_model import BaseConverter
from ..image_model import ImageModel
from ..rows_model import RowsModel
import re
import pytesseract
import cv2
import numpy as np

class Image2Rows(BaseConverter):
    def __init__(self, conf=None):
        self.conf = {"lang": "eng+rus", "psm": 4, "oem": 3, "k": 1, "onetone_delete": False}
        if conf is None:
            return
        for key, val in conf.items():
            if key in self.conf.keys():
                self.conf[key] = val

    def convert(self, input_model: ImageModel, output_model: RowsModel)-> None:
        row_list = self.extract_from_img(input_model.img)
        rows = []
        others = []
        for r in row_list:
            if re.match(r'^\s*$', r["text"]):
                others.append(r)
            else:
                rows.append(r)
        output_model.set_rows_from_dict(rows)
        output_model.set_others_from_dict(others)


    def extract_from_img(self, img):
        conf = self.conf
        dim = (conf["k"]*img.shape[1], conf["k"]*img.shape[0])
        img_ = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        tesseract_bboxes = pytesseract.image_to_data(
            config=f"-l {conf['lang']} --psm {conf['psm']} --oem {conf['oem']}",
            image=img_,
            output_type=pytesseract.Output.DICT)
        row_list = []
        st = -1
        for index_bbox, level in enumerate(tesseract_bboxes["level"]):
            if level == 4:
                st += 1
                x0 = round(tesseract_bboxes["left"][index_bbox]/conf["k"])
                y0 = round(tesseract_bboxes["top"][index_bbox]/conf["k"])
                w = round(tesseract_bboxes["width"][index_bbox]/conf["k"])
                h = round(tesseract_bboxes["height"][index_bbox]/conf["k"])
                # TODO: сделать фильтр ширины, поменять однотонный фильтер
                if conf["onetone_delete"] and np.var(img[y0:y0+h, x0:x0+w]) < 20:
                    continue
                row_list.append({
                    "text": ' ',
                    "x_top_left": x0,
                    "y_top_left": y0,
                    "width": w,
                    "height": h,
                })
                
            if level == 5:
                row_list[st]['text'] += ' '+ tesseract_bboxes['text'][index_bbox]
            
        
        row_list = self.size_filter(row_list)
        return row_list

    def size_filter(self, row_list):
        return [row for row in row_list if row["width"] >= 2 and row["height"] >= 2]