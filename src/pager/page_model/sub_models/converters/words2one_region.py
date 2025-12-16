from ..base_sub_model import BaseSubModel, BaseConverter
from ..dtype import ImageSegment, Block, Word, Region
from typing import List
from .words2rows import Words2Rows
from ..rows_model import RowsModel
from ..words_model import WordsModel
from ..region_model import RegionModel

class Words2OneRegion(BaseConverter):
    def convert(self, input_model: WordsModel, output_model: RegionModel)-> None:
        # word_list: List[Word] = input_model.words
        words2rows = Words2Rows()
        rows_model = RowsModel()
        if len(input_model.words) == 0:
            return
        
        words2rows.convert(input_model, rows_model)
    
        region = Region(rows_model.to_dict())
        
        region.set_label("text")
        output_model.set_regions([region])