from ..base_sub_model import BaseConverter
from ..pdf_model import PrecisionPDFModel
from ..words_model import WordsModel
from ..image_model import ImageModel
from ..dtype import Word
from typing import List
from .img_and_words2precision_pdf import ImageAndWords2PrecisionPDF
from .img2words import Image2Words
from ..exceptions import ConteinImage

class Image2PrecisionPDF(BaseConverter):
    def convert(self, input_model: ImageModel, output_model: PrecisionPDFModel):
        words_model = WordsModel()
        img2words = Image2Words()
        words_and_image2precision_pdf = ImageAndWords2PrecisionPDF()
        
        img2words.convert(input_model, words_model)
        words_model.img = input_model.img
        words_and_image2precision_pdf.convert(words_model, output_model)
