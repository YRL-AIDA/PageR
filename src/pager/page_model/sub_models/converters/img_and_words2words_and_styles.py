from ..base_sub_model import BaseConverter
from ..dtype import Word, Style
from ..exceptions import ConteinImage
from ..words_and_styles_model import WordsAndStylesModel
from ..words_model import WordsModel
from .model_scripts.model_20250121 import classifier_image_word, get_model
from .model_scripts.model_20250424 import classifier_image_word as classifier_image_word_new, get_model as get_model_new
import cv2
from typing import List 
import numpy as np

class ImageAndWords2WordsAndStyles(BaseConverter):
    def __init__(self, conf=None):
        if '20250121' in conf['path_model']: 
            self.model = get_model(conf["path_model"])
            self.classifier_image_word = lambda word_img:classifier_image_word(self.model, word_img).detach().numpy().tolist()
        elif '20250424' in conf['path_model']:
            self.model = get_model_new(conf["path_model"])
            self.classifier_image_word = lambda word_img:classifier_image_word_new(self.model, word_img).detach().numpy().tolist()
        else:
            print ("ERROR MODEL")
        

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
        
        
    
