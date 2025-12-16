from .pdf2img import PDF2Img
from .pdf2words import PDF2Words
from .pdf2rows import PDF2Rows

from .img2words import Image2Words

from .img2rows import Image2Rows

from .img2words_and_styles import Image2WordsAndStyles, Image2WordsAndStylesStatVec

from .pdf2words_and_styles import PDF2WordsAndStyles

from .pdf2only_fig_blocks import PDF2OnlyFigBlocks


from .words2one_region import Words2OneRegion

from .img_and_words2words_and_styles import ImageAndWords2WordsAndStyles

from .rows2region import Rows2Regions

from .words2rows import Words2Rows

# Delete
import warnings
class WordsToOneBlock(Words2OneRegion):
   def __init__(self):
       warnings.warn("use Words2OneRegion (WordsToOneBlock deleting)")
       super().__init__()

