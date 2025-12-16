import unittest
from pager import PageModel, PageModelUnit, WordsAndStylesModel, PDFModel, PDF2WordsAndStyles
import os

class TestWords2PhisModel(unittest.TestCase):
    pass
    # page = PageModel(page_units=[
    #     PageModelUnit(id="pdf_model", 
    #                   sub_model=PDFModel({'method':'w'}), 
    #                   extractors=[], 
    #                   converters={}),
    #     PageModelUnit(id="words_and_styles_model", 
    #                   sub_model=WordsAndStylesModel(), 
    #                   extractors=[], 
    #                   converters={"pdf_model": PDF2WordsAndStyles()})
    #     ])

    # page.read_from_file(os.path.join("files", "text_header_table.pdf"))
    # page.extract()
    # words_and_styles = page.to_dict()
        
    # def test_(self) -> None:
    #     keys = self.words_and_styles.keys()
    #     self.assertIn("words", keys)
    #     self.assertIn("styles", keys)

    # def test_count_style(self) -> None:
    #     words = self.words_and_styles
    #     self.assertEqual(len(self.words_and_styles['styles']), 4)
   
