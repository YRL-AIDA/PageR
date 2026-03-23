from pager.page_model.sub_models.dtype import Region, Row, Word, ImageSegment
from typing import List, Dict

class Page:
    def __init__(self, num_page, regions:List[Region]=None, rows:List[Row]=None, words:List[Word]=None, height=None, width=None):
        # TODO: fix info
        self.regions = regions
        self.rows = rows
        self.words = words
        self.set_regions_rows_words(regions, rows, words)
        self.num_page = num_page
        self.height = height
        self.width = width

    def set_regions_rows_words(self, regions:List[Region]=None, rows:List[Row]=None, words:List[Word]=None):
        self.regions = regions

        if rows is None and regions is not None:
            rows = [row for reg in regions for row in reg.rows]
        self.rows = rows
        
        if words is None and rows is not None:
            words = [word for row in rows for word in row.words]
        self.words = words

    def from_dict(self, data:Dict):
        self.num_page = data.get('number')
        self.width = data.get('width')
        self.height = data.get('height')

        regions =[Region(reg) for reg in data['regions']]  if 'regions' in data else None
        rows =[Row(rpw) for rpw in data['rows']]  if 'rows' in data else None
        words = [Word(word) for word in data['words']]  if 'words' in data else None

        self.set_regions_rows_words(regions, rows, words)
    
    @property
    def md(self):
        text = ""
        if self.regions is not None:
            for reg in self.regions:
                text += reg.md
            return text
        return text
                 
