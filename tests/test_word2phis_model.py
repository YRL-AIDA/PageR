import unittest
from pager import PageModel, PageModelUnit, WordsModel, PhisicalModel, WordsToOneBlock

class TestWords2PhisModel(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="words_model", 
                      sub_model=WordsModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="phisical_model", 
                      sub_model=PhisicalModel(), 
                      extractors=[], 
                      converters={"words_model": WordsToOneBlock()})
        ])

    page.read_from_file('files/words.json')
    page.extract()
    phis = page.to_dict()
        
    def test_count_blocks(self) -> None:
        self.assertEqual(len(self.phis['blocks']), 1)

    def test_count_words(self) -> None:
        self.assertEqual(len(self.phis['blocks'][0]['words']), 4, self.phis['blocks'][0]['words'])

    def test_size_blocks(self) -> None:
        x0 = self.phis['blocks'][0]['x_top_left']
        x1 = self.phis['blocks'][0]['x_bottom_right']
        y0 = self.phis['blocks'][0]['y_top_left']
        y1 = self.phis['blocks'][0]['y_bottom_right']
        self.assertEqual(x0, 46)
        self.assertEqual(x1, 183)
        self.assertEqual(y0, 41)
        self.assertEqual(y1, 94)
