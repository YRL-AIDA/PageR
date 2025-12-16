from ..base_sub_model import BaseConverter
from ..dtype import Word, Style
from ..exceptions import ConteinImage
from ..words_and_styles_model import WordsAndStylesModel
from ..words_model import WordsModel
import cv2
from typing import List 
import numpy as np
from pager.nn_models.manager_models import ManagerModels

class ImageAndWords2WordsAndStyles(BaseConverter):
    def __init__(self, conf=None):
        manager_models = ManagerModels()
        self.model, self.classifier_image_word = manager_models.get_model('style-model-20250121')
        

    def convert(self, input_model:WordsModel, output_model:WordsAndStylesModel):
        if not "img" in input_model.__dict__:
            raise ConteinImage()
        output_model.words, output_model.styles = self.separate(input_model.words, input_model.img)

    def separate(self, words:List[Word], img):
        styles = []
        words = [Word(word.to_dict()) for word in words]
        for word in words:
            try:
                word_img = cv2.cvtColor(word.segment.get_segment_from_img(img), cv2.COLOR_RGB2GRAY)/255
                tmp_style =  self.get_style_from_word(word_img, word)
                index_style = self._get_style(tmp_style, styles, delta_ = 0.1) 
            except:
                index_style = 0
                      
            if index_style == -1:
                styles.append(tmp_style)
                index_style = len(styles) - 1 
                tmp_style.id = index_style
            word.style_id =index_style
            
                
        
        return words, styles

    def _get_style(self, style: Style, styles: List[Style], delta_):
        for i, style_ in enumerate(styles):
            x1 = np.array(style_.font2vec)
            x2 = np.array(style.font2vec)
            if np.dot(x1-x2, x1-x2) < delta_:
                return i
        return -1
    
    def get_style_from_word(self, word_img, word):
        return Style({"id":None, "font2vec":self.classifier_image_word(word_img)})
        
        
    
