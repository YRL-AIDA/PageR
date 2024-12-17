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
    
def AP_and_AR_from_TP_FP_FN(TP, FP, FN):
    return TP/(TP+FP) if TP+FP != 0 else 0, TP/(TP+FN) if TP+FN != 0 else 0

def TP_FP_FN_UoI(true_segments: List[ImageSegment], pred_segments: List[ImageSegment], alpha=0.5):
    TP, FP, FN = 0,0,0
    pred_mask = np.zeros((len(pred_segments)))
    for i, pred_seg in enumerate(pred_segments):
        for true_seg in true_segments:
            UoI = segmenter_UoI([true_seg], [pred_seg])
            if UoI > pred_mask[i]:
                pred_mask[i] = UoI
        if pred_mask[i] > alpha:
            TP += 1
        elif pred_mask[i] == 0:
            FN += 1
        else:
            FP += 1
    return TP, FP, FN
