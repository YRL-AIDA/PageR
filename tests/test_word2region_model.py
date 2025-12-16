import unittest
from pager import PageModel, PageModelUnit, WordsModel, RowsModel, RegionModel, Words2Rows, Rows2Regions
import os
class TestWords2PhisModel(unittest.TestCase):
    page = PageModel(page_units=[
        PageModelUnit(id="words_model", 
                      sub_model=WordsModel(), 
                      extractors=[], 
                      converters={}),
        PageModelUnit(id="rows_model", 
                      sub_model=RowsModel(), 
                      extractors=[], 
                      converters={"words_model": Words2Rows()}),
        PageModelUnit(id="region_model", 
                      sub_model=RegionModel(),
                      extractors=[],
                      converters={"rows_model": Rows2Regions()})
        ])

    page.read_from_file(os.path.join('files','words.json'))
    page.extract()
    regions = page.to_dict()['regions']
        
    def test_count_blocks(self) -> None:
        self.assertEqual(len(self.regions), 2)

    def test_count_words(self) -> None:
        words = [word for reg in self.regions for row in reg['rows'] for word in row['words']]
        self.assertEqual(len(words), 4, self.regions)

    def test_size_blocks(self) -> None:
        x0 = self.regions[0]['x_top_left']
        x1 = self.regions[0]['x_bottom_right']
        y0 = self.regions[0]['y_top_left']
        y1 = self.regions[0]['y_bottom_right']
        self.assertEqual(x0, 46)
        self.assertEqual(x1, 183)
        self.assertEqual(y0, 41)
        self.assertEqual(y1, 58)
