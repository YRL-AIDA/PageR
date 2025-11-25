import unittest
from pager import PageModel, PageModelUnit, WordsAndStylesModel, PDFModel, WordsModel
from pager.page_model.sub_models.converters import PDF2Words
import os
class TestWords2PhisModel(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="pdf_model", 
                      sub_model=PDFModel({'method':'w'}), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_model", 
                      sub_model=WordsModel(), 
                      extractors=[], 
                      converters={"pdf_model": PDF2Words()})
        ])

    page.read_from_file(os.path.join("files", "text_header_table.pdf"))
    page.extract()
    words = page.to_dict()
        
    def test_(self) -> None:
        keys = self.words.keys()
        self.assertIn("words", keys)

    def test_count_words(self) -> None:
        with open(os.path.join("files", "text_header_table_text.txt"), "r", encoding="utf-8") as f:
            
            text = f.read().replace("\t", " ").replace("\n", " ")
            elements = text.split(" ")
            elements = [el for el in elements if el != '']
        words = [w['text'] for w in self.words['words']]
        self.assertEqual(words, elements)

    def test_style_word(self) -> None:
        word = self.words['words'][0]
        keys = word.keys()
        self.assertIn("bold", keys)
        self.assertIn("italic", keys)
        self.assertIn("font_name", keys)
        self.assertIn("size", keys)

        self.assertNotIn("style_id", keys)
    
        self.assertEqual(type(word["bold"]), float)
        self.assertIsNotNone(type(word["italic"]), float)
        self.assertIsNotNone(type(word["font_name"]), str)
        self.assertIsNotNone(type(word["size"]), int)

        self.assertEqual(word['text'], "Заголовок")

   
