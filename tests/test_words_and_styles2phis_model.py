import unittest
from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   WordsAndStylesToGNNBlocks)

class TestWordsAndStyles2PhisModel(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": ImageToWordsAndStyles()}),
        PageModelUnit(id="phisical_model", 
                      sub_model=PhisicalModel(), 
                      extractors=[], 
                      converters={"words_and_styles_model": WordsAndStylesToGNNBlocks()})
        ])

    page.read_from_file('files/segment_test.png')
    page.extract()
    phis = page.to_dict()
        
    def test_count_blocks(self) -> None:
        str_ = "/n".join([f"{i} - block: \t {b['text']}" for i, b in enumerate(self.phis['blocks'])])
        self.assertGreaterEqual(len(self.phis['blocks']), 3, )

