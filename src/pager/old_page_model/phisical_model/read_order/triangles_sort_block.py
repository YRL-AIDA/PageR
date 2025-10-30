from ..phisical_model import PhisicalModel
from ...base_sub_model import BaseExtractor
from ...dtype import Left2RightTop2BottomImageSegment

class TrianglesSortBlock(BaseExtractor):
    def extract(self, model: PhisicalModel):
        segs = [b.segment for b in model.blocks]
        inds = self.__sort_bboxes_using_triangles(segs)
        model.blocks = [model.blocks[i] for i in inds]

    def __sort_bboxes_using_triangles(self, segs):    
        
        for i in range(len(segs)):
            segs[i] = Left2RightTop2BottomImageSegment.converter(segs[i])
            segs[i].index = i
        
        for i in range(len(segs)):
            for j in range(len(segs)):
                if segs[j].greater_then_vertical(segs[i]):
                    segs[i], segs[j] = segs[j], segs[i]
                elif segs[j].greater_then_vertical(segs[i]) is None and segs[j].greater_then_horizont(segs[i]):
                    segs[i], segs[j] = segs[j], segs[i]
                    
        return  [seg.index for seg in segs]