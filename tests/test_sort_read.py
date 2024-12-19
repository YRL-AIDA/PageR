import unittest
import os
from pager import PageModel, PageModelUnit, PhisicalModel, WordsModel, WordsToOneBlock
from pager.page_model.sub_models.dtype.block import Block

class TestSort(unittest.TestCase):
    phis_model = PageModel([PageModelUnit("words", WordsModel(), extractors=[], converters={}),
                            PageModelUnit("block", PhisicalModel(), extractors=[], converters={"words": WordsToOneBlock()})])
    
    def test_sort_read1(self):
        block = self._get_block(os.path.join('files', 'unsorted_words.json'))
        block.sort_words()
        sorted_text = [w.text for w in block.words]
        self.assertEqual(sorted_text, ["1", "2", "3", "4", "5"], f"{sorted_text}")
    
    def test_sort_read2(self):
        block = self._get_block(os.path.join('files', 'unsorted_words2.json'))
        block.sort_words()
        sorted_text = [w.text for w in block.words]
        self.assertEqual(sorted_text, ["1", "2", "3", "4"], f"{sorted_text}")

    def _get_block(self, path) -> Block:
        self.phis_model.read_from_file(path)
        self.phis_model.extract()
        block = self.phis_model.page_units[-1].sub_model.blocks[0]
        return block
