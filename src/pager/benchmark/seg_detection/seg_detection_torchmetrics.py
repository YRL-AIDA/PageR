from ..base_benchmark import BaseBenchmark
from typing import Dict
import os 
import json
import time
import numpy as np
import torch
from torchmetrics.detection.mean_ap import MeanAveragePrecision
import cv2
from ...page_model.sub_models.dtype.image_segment import PositionException

COUNT_CLASS = 5
IOU_INTERVAL = np.arange(0.5, 1.0, 0.05)
COUNT_IOU_INTERVAL = len(IOU_INTERVAL)

class SegDetectionBenchmark(BaseBenchmark):
    def __init__(self, path_dataset, page_model, path_images=None, path_pdfs=None,
                 path_json=None, name="",save_dir=None, count_image=None, only_seg=False):
        self.path_dataset = path_dataset
        self.page_model = page_model
        self.path_pdfs = path_pdfs
        self.path_images = path_images
        self.path_json = path_json
        self.save_dir = save_dir
        self.count_image = count_image
        self.only_seg = only_seg
        super().__init__(name)
        
    def get_id_labels(self, label:str):
        if self.only_seg:
            return 0
        label = label.lower()
        if label in ("text", ):
            return 0
        elif label in ("header", "title"):
            return 1
        elif label in ("list", ):
            return 2
        elif label in ("table", ):
            return 3
        elif label in ("figure", "no_struct"):
            return 4

    def get_json_dataset(self):
        if self.path_json is None:
            json_dataset_path = [file for file in  os.listdir(self.path_dataset) if file.split(".")[-1] == "json"][0]
            path_ = os.path.join(self.path_dataset, json_dataset_path)
        else:
            path_ = self.path_json
        with open(path_) as f:
            json_dataset = json.load(f)
        return json_dataset
    
    def extract_from_json(self, json_dataset):
        self.CATEGORY = dict()
        for category in json_dataset["categories"]:
            self.CATEGORY[category["id"]] = category["name"]
        
        if self.count_image is None:
            self.count_image = len(json_dataset["images"])
        self.extract_image_true(json_dataset)
        self.extract_image_pred(json_dataset)

    def save_result_pred(self, json_dataset):
        os.mkdir(self.save_dir)
        for img in json_dataset["images"][:self.count_image]:
            save_path = os.path.join(self.save_dir, img["file_name"])
            self.save_rez_image(img, save_path, one_class=self.only_seg)
    
    def main_metric(self, json_dataset):
        target = [dict(     
                boxes=torch.tensor([an["bbox"] for an in  img["annotations_true"]]) ,
                labels=torch.tensor([an["category_id"] for an in  img["annotations_true"]]),
                ) for img in json_dataset["images"][:self.count_image]]
        preds = [dict(     
                boxes=torch.tensor([an["bbox"] for an in  img["annotations_pred"]]) ,
                scores=torch.tensor([1.0 for an in  img["annotations_pred"]]),
                labels=torch.tensor([an["category_id"] for an in  img["annotations_pred"]]),
                ) for img in json_dataset["images"][:self.count_image]]
        metric = MeanAveragePrecision(box_format="xywh")
        metric.update(preds, target)  
        rez = metric.compute()
        self.loger(f"mAP@IoU[0.50:0.95] = {rez['map']:.8f}")

    def start(self):
        json_dataset = self.get_json_dataset()
        self.extract_from_json(json_dataset)
        
        if self.save_dir is not None:
            self.save_result_pred(json_dataset)

        self.main_metric(json_dataset)

        time_ = np.mean([image["time"] for image in json_dataset["images"][:self.count_image]])
        self.loger(f"mean time: {time_ : .4f} sec.")

    def extract_image_pred(self, json_dataset):
        def in_not_content(block, content_block):
            xc = (block["x_top_left"]+block["x_bottom_right"])/2
            yc = (block["y_top_left"]+block["y_bottom_right"])/2
            return xc >= content_block["x_bottom_right"] or \
                   yc >= content_block["y_bottom_right"] or \
                   xc <= content_block["x_top_left"] or \
                   yc <= content_block["y_top_left"]
        
        
        def get_annotations_from_page(path, content_block ):
            self.page_model.read_from_file(path)
            start = time.time()
            self.page_model.extract()
            time_ = time.time() - start
            phis = self.page_model.to_dict()
            return [{"category_id": self.get_id_labels(block["label"]),
                     "bbox": [block["x_top_left"],
                              block["y_top_left"], 
                              block["x_bottom_right"]-block["x_top_left"],
                              block["y_bottom_right"]-block["y_top_left"]],
             } for block in phis["blocks"] if not in_not_content(block, content_block)], time_
        N = self.count_image
        for i, image_d in enumerate(json_dataset["images"][:self.count_image]):
            print(f"{(i+1)/N*100:.2f}%", end="\r")
            path = self.get_file(image_d["file_name"]) 
            an, time_ =  get_annotations_from_page(path, image_d["content_block"] )
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
                "category_id": self.get_id_labels(self.CATEGORY[true_block["category_id"]]),
                "bbox": true_block["bbox"],
            })

        for image_d in json_dataset["images"][:self.count_image]:
            x0 = min([block["bbox"][0] for block in image_d["annotations_true"]])
            y0 = min([block["bbox"][1] for block in image_d["annotations_true"]])
            x1 = max([block["bbox"][0]+block["bbox"][2] for block in image_d["annotations_true"]])
            y1 = max([block["bbox"][1]+block["bbox"][3] for block in image_d["annotations_true"]])
            image_d["content_block"] = {"x_top_left":x0,
                                        "y_top_left":y0, 
                                        "x_bottom_right":x1,
                                        "y_bottom_right":y1}
            
    def save_rez_image(self, img, save_path, one_class=False):
        def rect(mtrx, block, typeLine=4, line_size=0, c=None):
            colors = [
                (255, 0,   0),
                (255, 255, 0),
                (0,   255, 0),
                (0,   255, 255),
                (0,   0,   255)
            ]
            x0=int(block["bbox"][0])
            y0=int(block["bbox"][1])
            w=int(block["bbox"][2]) 
            h =int(block["bbox"][3])
            x1, y1 = x0 + w - 1, y0 + h -1
            color = colors[block["category_id"]] if c is None else c
           
            mtrx[y0-line_size:y0+line_size+1, [x for x in range(x0, x1) if x%4 < typeLine]] = color
            mtrx[y1-line_size:y1+line_size+1, [x for x in range(x0, x1) if x%4 < typeLine]] = color
            mtrx[[y for y in range(y0, y1) if y%4 < typeLine], x0-line_size:x0+line_size+1] = color
            mtrx[[y for y in range(y0, y1) if y%4 < typeLine], x1-line_size:x1+line_size+1] = color
        image_path = os.path.join(self.path_dataset if self.path_images is None else self.path_images, img["file_name"])
        mtrx = cv2.imread(image_path)
        mtrx = cv2.cvtColor(mtrx, cv2.COLOR_BGR2RGB)
        true_blocks = img["annotations_true"]
        pred_blocks = img["annotations_pred"]
        
        if one_class:
            for block in true_blocks:
                rect(mtrx, block, line_size=1, c=(0, 255, 0))
            for block in pred_blocks:
                rect(mtrx, block, c=(255, 0, 0))
        else:
            for block in true_blocks:
                rect(mtrx, block)
            for block in pred_blocks:
                rect(mtrx, block, typeLine=2)

        mtrx = cv2.cvtColor(mtrx, cv2.COLOR_RGB2BGR)
        cv2.imwrite(save_path, mtrx)

    def get_file(self, name):
        if self.path_pdfs is not None:
            return os.path.join(self.path_pdfs, name[:-4]+".pdf")
        elif self.path_images is not None:
            return os.path.join(self.path_images, name) 
        else:
            return os.path.join(self.path_dataset, name)
        