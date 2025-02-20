from ..base_sub_model import BaseSubModel
from typing import Dict
import numpy as np
import cv2
import matplotlib.pyplot as plt


class ImageModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.img: np.ndarray

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {}

    def read_from_file(self, path_file: str) -> None:
        self.img = self.__read(path_file)

    def clean_model(self) -> None:
        pass

    def __read(self, path):
        with open(path, "rb") as f:
            chunk = f.read()
        chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
        img_bgr = cv2.imdecode(chunk_arr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return img_rgb

    def show(self):
        plt.imshow(self.img)