from ..base_benchmark import BaseBenchmark
from typing import Dict
import os 
import json
import time
import numpy as np
import torch
from torchmetrics.detection.mean_ap import MeanAveragePrecision

LABELS = {
            "text": 0,
            "title": 1,
            "header": 1,
            "list": 2,
            "table": 3,
            "figure": 4,
            "no_struct":4,
        }
COUNT_CLASS = 5
IOU_INTERVAL = np.arange(0.5, 1.0, 0.05)
COUNT_IOU_INTERVAL = len(IOU_INTERVAL)

class SegDetectionBenchmark(BaseBenchmark):
    def __init__(self, path_dataset, page_model, path_images=None, path_json=None, name=""):
        self.path_dataset = path_dataset
        self.page_model = page_model
        self.path_images = path_images
        self.path_json = path_json
        super().__init__(name)

    def start(self):
        if self.path_json is None:
            json_dataset_path = [file for file in  os.listdir(self.path_dataset) if file.split(".")[-1] == "json"][0]
            path_ = os.path.join(self.path_dataset, json_dataset_path)
        else:
            path_ = self.path_json
        with open(path_) as f:
            json_dataset = json.load(f)
        
        self.CATEGORY = dict()
        self.NAME_CATEGORY_ID = dict()
        for category in json_dataset["categories"]:
            self.CATEGORY[category["id"]] = category["name"]
            self.NAME_CATEGORY_ID[category["name"]] = category["id"]

        self.extract_image_pred(json_dataset, self.page_model)
        self.extract_image_true(json_dataset)
    
        target = [dict(     
                boxes=torch.tensor([an["bbox"] for an in  img["annotations_true"]]) ,
                labels=torch.tensor([an["category_id"] for an in  img["annotations_true"]]),
                ) for img in json_dataset["images"]]
        preds = [dict(     
                boxes=torch.tensor([an["bbox"] for an in  img["annotations_pred"]]) ,
                scores=torch.tensor([1.0 for an in  img["annotations_pred"]]),
                labels=torch.tensor([an["category_id"] for an in  img["annotations_pred"]]),
                ) for img in json_dataset["images"]]
        metric = MeanAveragePrecision(box_format="xywh")
        metric.update(preds, target)   
        rez = metric.compute()
        # print(rez)
        self.loger(f"mAP@IoU[0.50:0.95] = {rez['map']:.8f}")

        time_ = np.mean([image["time"] for image in json_dataset["images"]])
        self.loger(f"mean time: {time_ : .4f} sec.")

    def extract_image_pred(self, json_dataset, page_model):
        def get_annotations_from_page(path):
            page_model.read_from_file(path)
            start = time.time()
            page_model.extract()
            time_ = time.time() - start
            phis = page_model.to_dict()
            return [{"category_id": self.NAME_CATEGORY_ID[block["label"]],
                     "bbox": [block["x_top_left"],
                              block["y_top_left"], 
                              block["x_bottom_right"]-block["x_top_left"],
                              block["y_bottom_right"]-block["y_top_left"]],
             } for block in phis["blocks"]], time_
        N = len(json_dataset["images"])
        for i, image_d in enumerate(json_dataset["images"]):
            print(f"{(i+1)/N*100:.2f}%", end="\r")
            path = os.path.join(self.path_dataset if self.path_images is None else self.path_images, image_d["file_name"])
            an, time_ =  get_annotations_from_page(path)
            image_d["annotations_pred"] = an
            image_d["time"] = time_

    def extract_image_true(self, json_dataset):
        id_to_index = dict()
        for index, image_d in enumerate(json_dataset["images"]):
            id_to_index[image_d["id"]] = index
            image_d["annotations_true"] = []
            
        for true_block in json_dataset["annotations"]:
            image_id = id_to_index[true_block["image_id"]]
            json_dataset["images"][image_id]["annotations_true"].append({
                "category_id": true_block["category_id"],
                "bbox": true_block["bbox"],
            })

        