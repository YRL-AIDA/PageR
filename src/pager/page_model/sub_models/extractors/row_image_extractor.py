from ..base_sub_model import BaseExtractor
from ..rows_model import RowsModel
from ..converters import PDF2OnlyFigBlocks
from ..pdf_model import PDFModel
from ..region_model import RegionModel
from ..exceptions import ConteinNumPage
from ..dtype import Word, Row, ImageSegment
import numpy as np


class ImageFromPDF(BaseExtractor):
    def __init__(self, pdf:PDFModel):
        # TODO block -> region
        self.pdf = pdf
        self.pdf2fig = PDF2OnlyFigBlocks()
        self.regions_fig = RegionModel()

    def extract(self, model: RowsModel):
        self.regions_fig.clean_model()
        self.pdf2fig.convert(self.pdf, self.regions_fig)
        img_rows = [Row(reg.to_dict()) for reg in self.regions_fig.regions]
        bool_matrix = np.array([
                        [
                            img_row_i.segment.is_intersection(img_row_j.segment)
                        for img_row_j in img_rows] 
                    for img_row_i in img_rows])
        new_bool_matrix = bool_matrix == None
        while (new_bool_matrix != bool_matrix).any():
            new_bool_matrix = bool_matrix.copy()
            bool_matrix = bool_matrix@bool_matrix
                        
        inds = np.array([i for i in range(len(img_rows))])

        blocks = []
        for _ in range(len(inds)):
            if len(inds) < 1:
                break
            i = np.argmin(inds)
            neig = inds[bool_matrix[i]]
            inds = inds[~bool_matrix[i]]
            blocks.append(neig)
            bool_matrix = bool_matrix[~bool_matrix[i], : ][:, ~bool_matrix[i]] 
            
        def get_row(regions):
            img_seg = ImageSegment(0,0,1,1)
            img_seg.set_segment_max_segments([r.segment for r in regions])
            row = Row({'segment': img_seg.get_segment_2p(), 'text':' '})
            return row

        img_rows = [
            get_row([img_rows[int(b)] for b in block])
            for block in blocks
        ]
        new_rows= []
        for row in model.rows:
            include=True
            for img_row in img_rows:
                if row.segment.is_intersection(img_row.segment):
                    img_row.segment.set_segment_max_segments([img_row.segment, row.segment])
                    include=False
            if include:  
                new_rows.append(row)
        
                    
        model.rows = new_rows+img_rows
        return bool_matrix