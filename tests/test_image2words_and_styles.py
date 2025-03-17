import unittest
from pager import PageModel, PageModelUnit, WordsAndStylesModel, ImageModel
from pager.page_model.sub_models.converters import Image2WordsAndStyles
from dotenv import load_dotenv
import os
load_dotenv(override=True)
STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]


class TestWords2PhisModel(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": Image2WordsAndStyles(conf={"path_model":STYLE_MODEL})})
        ])

    page.read_from_file("files/page.png")
    page.extract()
    words_and_styles = page.to_dict()
        
    def test_(self) -> None:
        keys = self.words_and_styles.keys()
        self.assertIn("words", keys)
        self.assertIn("styles", keys)

    def test_count_style(self) -> None:
        n = len(self.words_and_styles['styles'])
        m = len(self.words_and_styles['words'])
        self.assertGreaterEqual(n, 2, f"count styles: {n} < 2")
        self.assertLess(n, m/5, f"count styles: {n} > count word * 20% ({m/5})")
   
