from pager.page_model.sub_models.dtype import ImageSegment
from typing import List

def merge_segment(segs:List[ImageSegment]) -> List[int]:
    def _for(array_segs, array_ind):
        for ki, i in enumerate(array_ind):
            for kj, j in enumerate(array_ind):
                if i != j and array_segs[ki].is_intersection(array_segs[kj]):
                    array_segs[ki].set_segment_max_segments([array_segs[kj], array_segs[ki]])
                    array_segs[kj] = array_segs[ki]
                    array_ind[kj] = array_ind[ki]
                    
                    return True
        
        return False
    # Пока есть пересекающиеся прямоугольники, продолжаем объединение
    array_ind = [i for i in range(len(segs))]
    array_segs = [ImageSegment(dict_2p=seg.get_segment_2p()) for seg in segs]

    change = True
    while change:
        change = _for(array_segs, array_ind)
        
    new_ = dict()
    for i in array_ind:
        if not i in new_:
            new_[i] = len(new_.keys())
    array_ind = [new_[i] for i in array_ind]
    return array_ind