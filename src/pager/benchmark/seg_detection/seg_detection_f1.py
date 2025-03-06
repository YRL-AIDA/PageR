from ..base_benchmark import BaseBenchmark
from typing import Dict
import os 
import json
import time
import numpy as np
from .seg_detection_torchmetrics import (
    SegDetectionBenchmark as TorchSegDetectionBenchmark,
    COUNT_CLASS, 
    IOU_INTERVAL,
    COUNT_IOU_INTERVAL)

class SegDetectionBenchmark(TorchSegDetectionBenchmark):
    def main_metric(self, json_dataset):
        # return super().main_metric(json_dataset)
        if self.only_seg:
            count_class = 1
        else:
            count_class = COUNT_CLASS

        TPplusFN = np.zeros((count_class))
        TPplusFP = np.zeros((count_class))
        TPplusTP = np.zeros((count_class, COUNT_IOU_INTERVAL))
        IoU = [[] for _ in range(count_class)]

        Recall = np.zeros((count_class, COUNT_IOU_INTERVAL))
        Precision = np.zeros((count_class, COUNT_IOU_INTERVAL))
        F1 = np.zeros((count_class, COUNT_IOU_INTERVAL))
        
        for image in json_dataset["images"][:self.count_image]:
            TPplusFP_one_image, TPplusFN_one_image, IoU_one_image = self.calculate_metrics(image)
            for i in range(count_class):
                TPplusFP[i] += TPplusFP_one_image[i]
                TPplusFN[i] += TPplusFN_one_image[i]
                IoU[i] += IoU_one_image[i]
            
        for k, theta in enumerate(IOU_INTERVAL):
            for i, iou in enumerate(IoU):
                TPplusTP[i, k] = sum(np.array(iou) >= theta)
        
        for i in range(count_class):
            Precision[i] = TPplusTP[i] / TPplusFP[i] if TPplusFP[i] != 0 else 0.0
            Recall[i] = TPplusTP[i] / TPplusFN[i] if TPplusFN[i] != 0 else 0.0
        
        for i in range(count_class):
            self.loger(f"class {i} =======")
            for k, theta in enumerate(IOU_INTERVAL):
                self.loger(f"Precision (IoU={theta:.2f}): {Precision[i, k] : .8f}")
        for i in range(count_class):
            self.loger(f"class {i} =======")
            for k, theta in enumerate(IOU_INTERVAL):
                self.loger(f"Recall (IoU={theta:.2f}): {Recall[i, k] : .8f}")
        for i in range(count_class):
            self.loger(f"class {i} =======")
            for k, theta in enumerate(IOU_INTERVAL):
                f1 = 2*Precision[i, k]*Recall[i, k]/(Precision[i, k]+Recall[i, k]) if Precision[i, k]+Recall[i, k] != 0 else 0.0
                self.loger(f"F1 (IoU={theta:.2f}): {f1: .8f}")
        
        super().main_metric(json_dataset)
    
    def calculate_metrics(self, image):
        annotation_true = [[] for i in range(COUNT_CLASS)]
        annotation_pred = [[] for i in range(COUNT_CLASS)]

        for block_true in image["annotations_true"]:
            annotation_true[block_true["category_id"]].append(block_true["bbox"])

        for block_pred in image["annotations_pred"]:    
            annotation_pred[block_pred["category_id"]].append(block_pred["bbox"])

        TPplusFN = np.array([len(a) for a in annotation_true])
        TPplusFP = np.array([len(a) for a in annotation_pred])
        IoU = [[] for i in range(COUNT_CLASS)]

        for i in range(COUNT_CLASS):
            for bloc_pred in annotation_pred[i]:
                iou = np.max([self.calculate_iou(bloc_pred, block_true) for block_true in annotation_true[i]] + [0.0])
                                                                                                 # ^ если пусто, то 0.0
                IoU[i].append(iou)
                    
        return TPplusFP, TPplusFN, IoU
        
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
        