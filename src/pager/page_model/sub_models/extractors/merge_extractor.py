from ..base_sub_model import BaseExtractor
from ..dtype import Region, Row, ImageSegment
from ..region_model import RegionModel
from ..utils import merge_segment
from typing import List, Dict

class MergeExtractor(BaseExtractor):
    def extract(self, model: RegionModel):
        segs = [reg.segment for reg in model.regions]
        new_segs: Dict[int, List[int]] = dict()
        index_segs = merge_segment(segs)
        
        for ind_seg, ind_new_seg in enumerate(index_segs):
            if ind_new_seg in new_segs.keys():
                new_segs[ind_new_seg] = new_segs[ind_new_seg]+[ind_seg]
            else:
                new_segs[ind_new_seg] = [ind_seg]
        new_regions = []
        for segs_in_regions in new_segs.values():
            rows: List[Row] = []
            segment:ImageSegment = segs[segs_in_regions[0]]
            segment.set_segment_max_segments([segs[ind] for ind in segs_in_regions])
            label = model.regions[segs_in_regions[0]].label
            for ind in segs_in_regions:
                rows = rows + [row.to_dict() for row in model.regions[ind].rows]
            new_regions.append(Region({'rows': rows, 'segment': segment.get_segment_2p(), 'label': label}))
        model.regions = new_regions 