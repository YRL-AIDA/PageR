import unittest
from pager import (PageModel, PageModelUnit,
                   ImageModel, ImageToWordsAndStyles,
                   WordsAndStylesModel, PhisicalModel, 
                   WordsAndStylesToGNNBlocks)
from pager.page_model.sub_models.dtype import ImageSegment
from pager.metrics.uoi import segmenter_UoI as UoI

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

    page.read_from_file('files/UoI.png')
    page.extract()
    phis2 = page.to_dict()

    name_class = ["no_struct", "text", "header", "list", "table"]
    def test_count_blocks(self) -> None:
        str_ = "/n".join([f"{i} - block: \t {b['text']}" for i, b in enumerate(self.phis['blocks'])])
        self.assertGreaterEqual(len(self.phis['blocks']), 3, str_)

    def test_nead_class(self) -> None:
        for block in self.phis['blocks']:
            self.assertIn(block['label'], self.name_class, block['label'])

    def test_header_and_text(self) -> None:
        for block in self.phis['blocks']:
            if "ПРИМЕР" in block['text'].split():
                self.assertEqual(block['label'], 'header')
            if "Второй" in block['text'].split() or "Третий" in block['text'].split():
                self.assertEqual(block['label'], 'text')
    def test_uoi_classifier(self) -> None:
        seg_pred = [ImageSegment(dict_2p=b)for b in self.phis2['blocks']]
        seg_true = [ImageSegment(410, 50, 710, 110),
                    ImageSegment(30, 150, 410, 300),
                    ImageSegment(650, 150, 1060, 260),
                    ImageSegment(30, 350, 1030, 430)]
        
        UoI_rez = UoI(seg_pred, seg_true)
        self.assertGreaterEqual(UoI_rez, 0.5, f"UoI = {UoI_rez:.4f}")
