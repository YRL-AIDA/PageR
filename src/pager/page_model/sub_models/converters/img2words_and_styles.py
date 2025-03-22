from .img_and_words2words_and_styles import ImageAndWords2WordsAndStyles
from ..dtype import Word, Style
from ..words_and_styles_model import WordsAndStylesModel
from ..words_model import WordsModel
from ..image_model import ImageModel
from .img2words import Image2Words
import numpy as np


class Image2WordsAndStyles(ImageAndWords2WordsAndStyles):
    def __init__(self, conf=None):
        super().__init__(conf)
        self.img2words = Image2Words(conf)
        self.words_model = WordsModel()

    def convert(self, input_model:ImageModel, output_model:WordsAndStylesModel):
        self.img2words.convert(input_model, self.words_model)
        output_model.words, output_model.styles = self.separate(self.words_model.words, input_model.img)

class Image2WordsAndStylesStatVec(Image2WordsAndStyles):
    def __init__(self, conf=None):
        self.img2words = Image2Words(conf)
        self.words_model = WordsModel()

    def get_style_from_word(self, word_img, word):
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
        return Style({"id":None, "font2vec":vec_style})

import warnings

class ImageToWordsAndCNNStyles(Image2WordsAndStyles):
    def __init__(self, conf=None):
        warnings.warn("use Image2WordsAndStyles (ImageToWordsAndCNNStyles deleting)")
        super().__init__(conf)
       

    