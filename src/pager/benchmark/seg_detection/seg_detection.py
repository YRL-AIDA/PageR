from ..base_benchmark import BaseBenchmark, DocumentsBenchmark
from typing import Dict
import os 
import json
import time
import numpy as np
LABELS = {
            "text": 0,
            "header": 1,
            "list": 2, 
            "table": 3,
            "figure": 4,
        }

class SegDetectionBenchmark(BaseBenchmark):
    def __init__(self, path_dataset, page_model):
        self.path_dataset = path_dataset
        self.page_model = page_model
        super().__init__()
        

    def test_one_document(self, document) -> Dict[str, float]:
        rez = dict()
        json_true = document[0]
        path_img = document[1]
        start = time.time()

        self.page_model.read_from_file(path_img)
        self.page_model.extract()
        rez['time'] = time.time() - start
        json_rez = self.page_model.to_dict()
        json_pred = {
            "bbox": [[seg["x_top_left"],seg["y_top_left"], seg["x_bottom_right"]-seg["x_top_left"],seg["y_bottom_right"]-seg["y_top_left"]] for seg in json_rez["blocks"]],
            "category_id": [LABELS[seg["label"]] for seg in json_rez["blocks"]]
        }
        mAP=  self.mAP_IoU(json_true, json_pred)
        rez['mAP @ IoU=0.5'] = mAP[0]
        rez['mAP @ IoU=0.5 (text)'] = mAP[1][0]
        rez['mAP @ IoU=0.5 (header)'] = mAP[1][1]
        rez['mAP @ IoU=0.5 (list)'] = mAP[1][2]
        rez['mAP @ IoU=0.5 (table)'] = mAP[1][3]
        rez['mAP @ IoU=0.5 (figure)'] = mAP[1][4]
        return rez
    
    def mAP_IoU(self, json_true, json_pred, iou_threshold=0.5, num_classes=5):
        gt_boxes = json_true['bbox']
        gt_categories = json_true['category_id']

        pred_boxes = json_pred['bbox']
        pred_categories = json_pred['category_id']

        # Initialize list to store AP for each class
        aps = []

        # Calculate AP for each class
        for class_id in range(num_classes):
            # Filter boxes and categories for the current class
            gt_boxes_class = [box for box, cat in zip(gt_boxes, gt_categories) if cat == class_id]
            gt_categories_class = [cat for cat in gt_categories if cat == class_id]

            pred_boxes_class = [box for box, cat in zip(pred_boxes, pred_categories) if cat == class_id]
            pred_categories_class = [cat for cat in pred_categories if cat == class_id]

            if len(gt_boxes_class) != 0 or len(pred_boxes_class) != 0:
            # Calculate AP for the current class
                ap = self.calculate_ap(gt_boxes_class, gt_categories_class, pred_boxes_class, pred_categories_class, iou_threshold)
            else:
                ap = None
            aps.append(ap)

        # Calculate mAP as the mean of APs
        mAP = np.mean([ap for ap in aps if ap != None]) if len(aps) != 0 else 1
        return mAP, aps

    def calculate_ap(self, gt_boxes, gt_categories, pred_boxes, pred_categories, iou_threshold=0.5):
        # Initialize variables for AP calculation
        tp = np.zeros(len(pred_boxes))
        fp = np.zeros(len(pred_boxes))

        # Match predictions to ground truth
        for i, pred_box in enumerate(pred_boxes):
            max_iou = 0
            best_gt_idx = -1

            for j, gt_box in enumerate(gt_boxes):
                if gt_categories[j] == pred_categories[i]:
                    iou = self.calculate_iou(pred_box, gt_box)
                    if iou > max_iou:
                        max_iou = iou
                        best_gt_idx = j

            if max_iou >= iou_threshold:
                tp[i] = 1
            else:
                fp[i] = 1

        # Calculate Precision and Recall
        tp_cumsum = np.cumsum(tp)
        fp_cumsum = np.cumsum(fp)

        precision = tp_cumsum / (tp_cumsum + fp_cumsum)
        recall = tp_cumsum / len(gt_boxes)

        # Calculate AP (Area under Precision-Recall curve)
        ap = 0
        for t in np.arange(0, 1.1, 0.1):
            if np.sum(recall >= t) == 0:
                p = 0
            else:
                p = np.max(precision[recall >= t])
            ap += p / 11

        return ap

    def calculate_iou(self, box1, box2):
        # box = [x, y, width, height]
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        # Calculate intersection area
        inter_x1 = max(x1, x2)
        inter_y1 = max(y1, y2)
        inter_x2 = min(x1 + w1, x2 + w2)
        inter_y2 = min(y1 + h1, y2 + h2)

        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

        # Calculate union area
        box1_area = w1 * h1
        box2_area = w2 * h2
        union_area = box1_area + box2_area - inter_area

        # Calculate IoU
        iou = inter_area / union_area if union_area > 0 else 0
        return iou

    def get_documents(self) -> DocumentsBenchmark:
        return SegDetectionDocumentsBenchmark(self.path_dataset)

class SegDetectionDocumentsBenchmark(DocumentsBenchmark):
    def __init__(self, path):
        path_pred = os.path.join(path, 'images')
        self.name_images = os.listdir(path_pred)
        self.path_preds = [os.path.join(path_pred, p) for p in self.name_images]
        super().__init__(len(self.path_preds))
        with open(os.path.join(path, 'result.json'), "r") as f:
            self.result = json.load(f)
        
        self.id_images = self.__get_id_image(self.result["images"], self.name_images)
        self.segs_for_id = [self.__get_json_segs(self.result["annotations"], i) for i in self.id_images]
        LABELS_FILES = dict()
        for l in self.result["categories"]:
            LABELS_FILES[l["id"]] = l["name"]
        
        
        self.trues = [{
            "bbox": [seg["bbox"] for seg in segs] ,
            "category_id": [LABELS[LABELS_FILES[seg["category_id"]]] for seg in segs]
        } for segs in self.segs_for_id]
        
    

    def get_i_true(self):
        return self.trues[self.i]

    def get_i_pred(self):
        return self.path_preds[self.i]
    
    def __get_id_image(self, json_images, name_images):
        id_images = []
        for img in name_images:
            for image_d in json_images:
                img_code = image_d["file_name"].split('/')[1]
                if img_code == img:
                    id_images.append(image_d["id"])
        return id_images
    
    def __get_json_segs(self, json_segs, id_image):
        segs = []
        for seg in json_segs:
            if seg["image_id"] == id_image:
                segs.append(seg)
        
        return segs
        