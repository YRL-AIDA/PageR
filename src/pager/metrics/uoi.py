from pager.page_model.sub_models.dtype.image_segment import ImageSegment
from typing import List
import numpy as np

def segmenter_UoI(true_segments: List[ImageSegment], pred_segments: List[ImageSegment]):
    
    big_segment = ImageSegment(0, 0, 1, 1)
    big_segment.set_segment_max_segments(true_segments+pred_segments)
    dict_big = big_segment.get_segment_2p()
    N, M = dict_big['x_bottom_right'], dict_big['y_bottom_right']
    true_mtrx = np.zeros((M, N), dtype=np.bool_)
    pred_mtrx = np.zeros((M, N), dtype=np.bool_)
    for mtrx, segs in zip([true_mtrx, pred_mtrx], [true_segments, pred_segments]):
        for seg in segs:
            dict_seg = seg.get_segment_2p()
            x0 = dict_seg['x_top_left'] 
            y0 = dict_seg['y_top_left'] 
            x1 = dict_seg['x_bottom_right'] 
            y1 = dict_seg['y_bottom_right']
            mtrx[y0:y1, x0:x1] = 1
    num1 = (true_mtrx & pred_mtrx).sum()
    num2 = (true_mtrx | pred_mtrx).sum()
    return num1/num2 if num2 != 0 else 1.
    
