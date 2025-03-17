from .img_and_words2words_and_styles import ImageAndWords2WordsAndStyles
from ..words_and_styles_model import WordsAndStylesModel
from ..words_model import WordsModel
from ..image_model import ImageModel
from .pdf2words import PDF2Words
from .pdf2img import PDF2Img
from .model_scripts.model_20250121 import classifier_image_word
from ..dtype import Style
from typing import List

class PDF2WordsAndStyles(ImageAndWords2WordsAndStyles):
    def __init__(self, conf=None):
        super().__init__(conf)
        self.pdf2words = PDF2Words()
        self.words_model = WordsModel()
        self.img_model = ImageModel()
        self.pdf2img = PDF2Img()

    def convert(self, input_model:ImageModel, output_model:WordsAndStylesModel):
        self.pdf2img.convert(input_model, self.img_model)
        self.pdf2words.convert(input_model, self.words_model)
        output_model.words, output_model.styles = self.separate(self.words_model.words, self.img_model.img)
    
    def _get_style(self, style: Style, styles: List[Style], delta_):
        for i, style_ in enumerate(styles):
            if style_.font_type == style.font_type:
                return i
        style.font2vec = classifier_image_word(self.model, style.img_font).detach().numpy().tolist()
        del style.img_font
        return -1
    
    def get_style_from_word(self, word_img, word):
        style = Style({"id":None, "font_type": word.font_name})
        style.img_font = word_img # обработка идет только для уникальных картинок
        return style
#     def get_style_from_word(self, word):
#         name  = word["font_type"].lower()
#         mono = 0 if "mono" in name else 1
#         serif = 1
#         for ind in SANS:
#             if ind in name:
#                 serif = 0 
#                 break
#         bold = 2 if word["bold"] else 1
#         return {"font2vec": [serif, mono, bold] }

# SANS = ["sans", 'agency', 'grotesk', 'christian',
#  'andalé', 'antique', 'aptos', 'arial',
#  'arial', 'austria', 'itc', 'avenir',
#  'bahnschrift', 'bank', 'bell',  'benguiat',
#  'breeze', 'calibri', 'candara',  'cantarell',
#  'caractères',  'century', 'charcoal', 'chicago',
#  'adobe', 'clearview', 'comic',  'consolas',
#  'corbel', 'ff', 'dejavu',  'din',
#  'drogowskaz',  'droid', 'dubai',  'eras',
#  'eurostile', 'fira',  'folio',
#  'franklin',  'frutiger', 'futura', 'geneva',
#  'gerstner', 'gill', 'gotham', 'grand',
#  'haettenschweiler',  'handel', 'harmonyos', 'helvetica',
#  'highway', 'ibm', 'impact', 'interstate',
#  'roboto', 'johnston', 'kabel', 'karrik',
#  'klavika', 'lato', 'liberation',  'franklin',
#  'linux', 'lucida', 'lucida', 'fs',
#  'ff', 'ms', 'montserrat', 'myriad',
#  'national', 'news', 'neuzeit', 'nokia',
#  'noto', 'nunito', 'ocr-b', 'open',
#  'optima', 'overpass', 'mark', 'radis',
#  'rail', 'roboto', 'san', 'ff',
#  'segoe',  'microsoft', 'seravek',  'skia',
#  'oneplus', 'snv', 'nikolas', 'source',
#  'sweden', 'syntax', 'tahoma', 'thesis',
#  'tiresias', 'trade', 'transport', 'tratex',
#  'trebuchet', 'twentieth', 'ubuntu', 'unica',
#  'univers', 'vag', 'bitstream', 'vercetti',
#  'verdana', 'whitney']