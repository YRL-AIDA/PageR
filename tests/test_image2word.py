import unittest
from pager import PageModel, PageModelUnit, ImageModel, WordsModel, Image2Words

class TestImage2Words(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="image_model", 
                      sub_model=ImageModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="words_model", 
                      sub_model=WordsModel(), 
                      extractors=[], 
                      converters={"image_model": Image2Words()})
        ])


    def test_no_word(self) -> None:
        self.page.read_from_file('files/notext.png')
        self.page.extract()
        rez = self.page.to_dict()
        self.assertEqual(len(rez['words']), 0)


    def test_one_word(self) -> None:
        self.page.read_from_file('files/oneword.png')
        self.page.extract()
        rez = self.page.to_dict()
        self.assertEqual(len(rez['words']), 1)
        self.assertEqual(rez['words'][0]['text'], 'Слово')

    def test_text(self) -> None:
        self.page.read_from_file('files/easytext.png')
        self.page.extract()
        rez = self.page.to_dict()
        self.assertEqual(len(rez['words']), 56)


