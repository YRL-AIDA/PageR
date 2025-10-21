import unittest
# from pager import (PageModel, PageModelUnit,
#                    ImageModel, Image2WordsAndStyles,
#                    WordsAndStylesModel, PhisicalModel, 
#                    WordsToDBSCANBlocks)
# from pager.page_model.sub_models.dtype import ImageSegment
# from pager.metrics.uoi import segmenter_UoI as UoI, AP_and_AR_from_TP_FP_FN, TP_FP_FN_UoI
# from dotenv import load_dotenv
import os
# load_dotenv(override=True)
# STYLE_MODEL = os.environ["PATH_STYLE_MODEL"]

from pager.page_model.sub_models.converters import Rows2Regions
from pager import RegionModel, RowsModel

class TestRowGLAM(unittest.TestCase):
    rows2region = Rows2Regions()

    region_model = RegionModel()
    file_name = os.path.join('files','regions.json')
    region_model.read_from_file(file_name)
    rows = [row.to_dict() for reg in region_model.regions for row in reg.rows]
    rows_model = RowsModel()
    rows_model.from_dict({"rows": rows})

    region_model = RegionModel()
    def test_convert(self):
        self.rows2region.convert(self.rows_model, self.region_model)
    # page = PageModel(page_units=[
    #     PageModelUnit(id="image_model", 
    #                   sub_model=ImageModel(), 
    #                   extractors=[], 
    #                   converters={}),
    #     PageModelUnit(id="words_and_styles_model", 
    #                   sub_model=WordsAndStylesModel(), 
    #                   extractors=[], 
    #                   converters={"image_model": Image2WordsAndStyles({"path_model": STYLE_MODEL})}),
    #     PageModelUnit(id="phisical_model", 
    #                   sub_model=PhisicalModel(), 
    #                   extractors=[], 
    #                   converters={"words_and_styles_model": WordsToDBSCANBlocks()})
    #     ])

    # page.read_from_file('files/segment_test.png')
    # page.extract()
    # phis = page.to_dict()    

    # page.read_from_file('files/UoI.png')
    # page.extract()
    # phis2 = page.to_dict()
    # seg_pred = [ImageSegment(dict_2p=b)for b in phis2['blocks']]
    # seg_true = [ImageSegment(410, 50, 710, 110),
    #                 ImageSegment(30, 150, 410, 300),
    #                 ImageSegment(650, 150, 1060, 260),
    #                 ImageSegment(30, 350, 1030, 430)]
        
    # AP, AR = AP_and_AR_from_TP_FP_FN(*TP_FP_FN_UoI(seg_pred, seg_true))
    # UoI_rez = UoI(seg_pred, seg_true)
    # name_class = ["no_struct", "text", "header", "list", "table"]
    # def test_count_blocks(self) -> None:
    #     str_ = "/n".join([f"{i} - block: \t {b['text']}" for i, b in enumerate(self.phis['blocks'])])
    #     self.assertGreaterEqual(len(self.phis['blocks']), 3, str_)

    # def test_nead_class(self) -> None:
    #     for block in self.phis['blocks']:
    #         self.assertIn(block['label'], self.name_class, block['label'])

    # def test_header_and_text(self) -> None:
    #     for block in self.phis['blocks']:
    #         if "ПРИМЕР" in block['text'].split():
    #             self.assertEqual(block['label'], 'header')
    #         if "Второй" in block['text'].split() or "Третий" in block['text'].split():
    #             self.assertEqual(block['label'], 'text')
    # def test_uoi_classifier(self) -> None:
    #     self.assertGreaterEqual(self.UoI_rez, 0.5, f"UoI = {self.UoI_rez:.4f}")
        
    # def test_AP(self) -> None:
    #     self.assertGreaterEqual(self.AP, 0.5, f"AP = {self.AP:.6f}")

    # def test_AR(self) -> None:
    #     self.assertGreaterEqual(self.AR, 0.5, f"AR = {self.AR:.6f}")
