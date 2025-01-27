import unittest
from pager import PageModel, PageModelUnit, WordsAndStylesModel, ImageModel, ImageToWordsAndCNNStyles
import os

PATH_STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]
class TestWords2PhisModel(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_and_styles_model", 
                      sub_model=WordsAndStylesModel(), 
                      extractors=[], 
                      converters={"image_model": ImageToWordsAndCNNStyles(conf={"path_model": PATH_STYLE_MODEL })})
        ])

    page.read_from_file("files/page.png")
    page.extract()
    words_and_styles = page.page_units[-1].sub_model.to_dict(is_vec=True)
    
    def test_size_nodes_feature_4n(self) -> None:
        styles = self.words_and_styles["styles"]
        style = styles[0]["font2vec"]
        #  STYLE=3 + POSITION=2
        self.assertEqual(len(style), 3, f"Count nodes = {len(style)}")