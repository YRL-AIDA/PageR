from .seg_detection_f1 import SegDetectionBenchmark as SegDetectionBenchmarkF1
import time
from pager.page_model.sub_models.dtype import ImageSegment, Word
import numpy as np

class SegDetectionBenchmark(SegDetectionBenchmarkF1):
    def extract_from_json(self, json_dataset):
        self.CATEGORY = dict()
        for category in json_dataset["categories"]:
            self.CATEGORY[category["id"]] = category["name"]
        
        if self.count_image is None:
            self.count_image = len(json_dataset["images"])
        
        self.extract_image_true_and_pred(json_dataset)
        # self.extract_image_true(json_dataset)
    
    def extract_image_true_and_pred(self, json_dataset):
        id_to_index = dict()
        for index, image_d in enumerate(json_dataset["images"]):
            id_to_index[image_d["id"]] = index
            image_d["annotations_true"] = []
            
        for true_block in json_dataset["annotations"]:
            image_id = id_to_index[true_block["image_id"]]
            json_dataset["images"][image_id]["annotations_true"].append({
                "category_id": self.get_id_labels(self.CATEGORY[true_block["category_id"]]),
                "bbox": true_block["bbox"],
                "word_ids":[]
            })


        def get_annotations_from_page(path, image_d):
            self.page_model.read_from_file(path)
            start = time.time()
            self.page_model.extract()
            time_ = time.time() - start
            phis = self.page_model.to_dict()
            words = [Word(w).segment for b in phis['blocks'] for w in b['words']]
            
            true_blocks = [ImageSegment(int(b['bbox'][0]), 
                                        int(b['bbox'][1]),
                                        int(b['bbox'][0]+b['bbox'][2]),
                                        int(b['bbox'][1]+b['bbox'][3])) for b in image_d["annotations_true"] ]
            delete_words = []
            for j, word in enumerate(words): 
                is_delete = True
                for i, b in enumerate(true_blocks):
                    if word.is_intersection(b):
                       image_d["annotations_true"][i]["word_ids"].append(j)
                       is_delete=False
                       break 
                if is_delete:
                    delete_words.append(j)

            pred_blocks = [{"category_id": self.get_id_labels(block["label"]),
                     "bbox": [block["x_top_left"],
                              block["y_top_left"], 
                              block["x_bottom_right"]-block["x_top_left"],
                              block["y_bottom_right"]-block["y_top_left"]],
                    "word_ids": []
            } for block in phis["blocks"]]
            pred_segments = [ImageSegment(int(b['bbox'][0]), 
                                          int(b['bbox'][1]),
                                          int(b['bbox'][0]+b['bbox'][2]),
                                          int(b['bbox'][1]+b['bbox'][3])) for b in pred_blocks ]
            exist_block = []
            for j, word in enumerate(words): 
                for i, b in enumerate(pred_segments):
                    if word.is_intersection(b):
                        if not j in delete_words:
                            pred_blocks[i]["word_ids"].append(j)
                            exist_block.append(i)
                            break 
            rez = [pred_blocks[i] for i in list(set(exist_block))]
            return rez, time_
        
        N = self.count_image
        for i, image_d in enumerate(json_dataset["images"][:self.count_image]):
            print(f"{(i+1)/N*100:.2f}%", end="\r")
            path = self.get_file(image_d["file_name"]) 
            an, time_ =  get_annotations_from_page(path, image_d)
            image_d["annotations_pred"] = an
            image_d["time"] = time_

            new_pred = []
            for an in image_d["annotations_pred"]:
                if len(an['word_ids']) != 0:
                    new_pred.append(an)
            image_d["annotations_pred"] = new_pred

            new_true = []
            for an in image_d["annotations_true"]:
                if len(an['word_ids']) != 0:
                    new_true.append(an)
            image_d["annotations_true"] = new_true

           


        


        

        # for image_d in json_dataset["images"][:self.count_image]:
        #     x0 = min([block["bbox"][0] for block in image_d["annotations_true"]])
        #     y0 = min([block["bbox"][1] for block in image_d["annotations_true"]])
        #     x1 = max([block["bbox"][0]+block["bbox"][2] for block in image_d["annotations_true"]])
        #     y1 = max([block["bbox"][1]+block["bbox"][3] for block in image_d["annotations_true"]])
        #     image_d["content_block"] = {"x_top_left":x0,
        #                                 "y_top_left":y0, 
        #                                 "x_bottom_right":x1,
        #                                 "y_bottom_right":y1}


    def calculate_metrics(self, image, count_class):
        annotation_true = [[] for i in range(count_class)]
        annotation_pred = [[] for i in range(count_class)]

        for block_true in image["annotations_true"]:
            annotation_true[block_true["category_id"]].append(block_true["word_ids"])

        for block_pred in image["annotations_pred"]:    
            annotation_pred[block_pred["category_id"]].append(block_pred["word_ids"])

        TPplusFN = np.array([len(a) for a in annotation_true])
        TPplusFP = np.array([len(a) for a in annotation_pred])
        IoU = [[] for i in range(count_class)]

        for i in range(count_class):
            for bloc_pred in annotation_pred[i]:
                iou = np.max([self.calculate_word_iou(bloc_pred, block_true) for block_true in annotation_true[i]] + [0.0])
                                                                                                 # ^ если пусто, то 0.0
                IoU[i].append(iou)
                    
        return TPplusFP, TPplusFN, IoU
    
    def calculate_word_iou(self, box1, box2):
        a = set(box1)
        b = set(box2)           
        i = len(a&b)
        u = len(a|b)
        return i/u if u!=0 else 0