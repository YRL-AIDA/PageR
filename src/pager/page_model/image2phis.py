from .page_model import PageModel, PageModelUnit
from .sub_models import ImageModel, WordsModel, PhisicalModel, ImageToWords, WordsToOneBlock

class Image2Phis(PageModel):
    def __init__(self):
        super().__init__(page_units=[
            PageModelUnit(id="image_model", 
                          sub_model=ImageModel(), 
                          extractors=[], 
                          converters={}),
            PageModelUnit(id="words_model", 
                          sub_model=WordsModel(), 
                          extractors=[], 
                          converters={"image_model": ImageToWords()}),
            PageModelUnit(id="phisical_model", 
                          sub_model=PhisicalModel(), 
                          extractors=[], 
                          converters={"words_model": WordsToOneBlock()})
        ])