from ..base_sub_model import BaseConverter
from ..pdf_model import PrecisionPDFModel
from ..words_model import WordsModel
from ..dtype import Word
from typing import List
from ..exceptions import ConteinImage

class ImageAndWords2PrecisionPDF(BaseConverter):
    def convert(self, input_model: WordsModel, output_model: PrecisionPDFModel):
        if not "img" in input_model.__dict__:
            raise ConteinImage()
        h, w = input_model.img.shape[:2]
        precision_json = {
            "pages": [
                {
                "number": 0,
                "tables": [],
                "images": [],
                "width": w,
                "words": [
                    {
                    "x_top_left": w.segment.x_top_left,
                    "y_top_left": w.segment.y_top_left,
                    "width": w.segment.width,
                    "text": w.text,
                    "height": w.segment.height
                    } for w in input_model.words]
               ,
                "height": h
                },
            ]
        }
        output_model.pdf_json = precision_json

