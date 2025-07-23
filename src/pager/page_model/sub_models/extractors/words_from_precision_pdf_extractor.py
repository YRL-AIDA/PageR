from ..base_sub_model import BaseExtractor
from ..pdf_model import PrecisionPDFModel
from ..words_model import WordsModel
from ..exceptions import ConteinNumPage
from ..dtype.block import Word


class WordsFromPrecisionPDFExtractor(BaseExtractor):
    def __init__(self, precision_pdf:PrecisionPDFModel):
        self.precision_pdf = precision_pdf
        if not "num_page" in self.precision_pdf.__dict__:
            raise ConteinNumPage()

    def extract(self, model:WordsModel):
        json_words = self.precision_pdf.pdf_json["pages"][self.precision_pdf.num_page]['words']
        word_list = self.get_words(json_words)
        model.words = word_list

    def get_words(self, words_json):
        words = []
        for word in words_json:
            if word["height"] < 1 or word["width"] < 1:
                continue
            word["segment"] = word 
            words.append(Word(word))
        return words