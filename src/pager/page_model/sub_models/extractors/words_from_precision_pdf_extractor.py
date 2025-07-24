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
        json_pdf = self.precision_pdf.to_dict()
        json_words = json_pdf["pages"][self.precision_pdf.num_page]['words']
        word_list = self.get_words(json_words)
        model.words = word_list

    def get_words(self, words_json:list[dict]):
        words = []
        for word in words_json:
            word_dict = word.copy()
            if word_dict["height"] < 1 or word_dict["width"] < 1:
                continue
            word_dict["segment"] = word_dict 
            words.append(Word(word_dict))
        return words