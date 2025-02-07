from ..base_benchmark import BaseBenchmark
from typing import Dict
import os 
import json
import time
import numpy as np
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
        
        TPplusFN = np.zeros(COUNT_CLASS)
        TPplusFP = np.zeros(COUNT_CLASS)
        TPplusTP = np.zeros((COUNT_CLASS, COUNT_IOU_INTERVAL))
        IoU = [[] for i in range(COUNT_CLASS)]
        Recall = np.zeros((COUNT_CLASS, 10))
        Precision = np.zeros((COUNT_CLASS, 10))
        
        for image in json_dataset["images"]:
            TPplusFP_one_image, TPplusFN_one_image, IoU_one_image = self.calculate_metrics(image)
            for i in range(COUNT_CLASS):
                TPplusFP[i] += TPplusFP_one_image[i]
                TPplusFN[i] += TPplusFN_one_image[i]
                IoU[i] += IoU_one_image[i]
            
        for k, theta in enumerate(IOU_INTERVAL):
            for i, iou in enumerate(IoU):
                TPplusTP[i, k] = sum(np.array(iou) >= theta)
       
        for i in range(COUNT_CLASS):
            Precision[i] = TPplusTP[i] / TPplusFP[i] if TPplusFP[i] != 0 else 0.0
            Recall[i] = TPplusTP[i] / TPplusFN[i] if TPplusFN[i] != 0 else 0.0
        AP = np.zeros(COUNT_CLASS)
        for i in range(COUNT_CLASS):
            p = Precision[i]
            r = Recall[i]
            ind = np.argsort(r)
            AP[i] = np.trapezoid(p[ind], x=r[ind])
        for name, ind in LABELS.items():
            self.loger(f"AP@IoU[0.50:0.95] ({name}) = {AP[ind]:.4f}")
        self.loger(f"mAP@IoU[0.50:0.95] = {np.mean(AP):.4f}") 

        time_ = np.mean([image["time"] for image in json_dataset["images"]])
        self.loger(f"mean time: {time_ : .4f} sec.")
    
    def calculate_metrics(self, image):
        annotation_true = [[] for i in range(COUNT_CLASS)]
        annotation_pred = [[] for i in range(COUNT_CLASS)]
        def get_index_from_block(block):
            category_id = block["category_id"]
            label = self.CATEGORY[category_id]
            return LABELS[label]

        for block_true in image["annotations_true"]:
            annotation_true[get_index_from_block(block_true)].append(block_true["bbox"])

        for block_pred in image["annotations_pred"]:    
            annotation_pred[get_index_from_block(block_pred)].append(block_pred["bbox"])

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

        