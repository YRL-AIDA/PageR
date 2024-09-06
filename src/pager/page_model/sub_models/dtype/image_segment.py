from abc import ABC
import numpy as np

from typing import Dict, List
import matplotlib.pyplot as plt 

class ImageSegment(ABC):
    def __init__(self, x_top_left=None, y_top_left=None, x_bottom_right=None, y_bottom_right=None, dict_2p=None, dict_p_size=None):
        if dict_2p is not None:
            self.set_segment_2p(dict_2p)
        elif dict_p_size is not None:
            self.set_segment_p_size(dict_p_size)
        else:
            self._set_segment(x_top_left, y_top_left, x_bottom_right, y_bottom_right)
        self.info = dict()

    def get_segment_from_img(self, img: np.ndarray, delta=0):
        h0 = self.y_top_left - delta
        h1 = self.y_bottom_right +  delta
        w0 = self.x_top_left - delta
        w1 = self.x_bottom_right + delta
        return img[h0:h1, w0:w1, :] if len(img.shape) == 3 else img[h0:h1, w0:w1]

    def get_segment_2p(self):
        return {
            "x_top_left": self.x_top_left,
            "x_bottom_right": self.x_bottom_right,
            "y_top_left": self.y_top_left,
            "y_bottom_right": self.y_bottom_right
        }

    def get_height(self):
        return self.y_bottom_right-self.y_top_left

    def get_width(self):
        return self.x_bottom_right - self.x_top_left

    def get_center(self):
        x_c = round((self.x_top_left + self.x_bottom_right) / 2)
        y_c = round((self.y_top_left + self.y_bottom_right) / 2)
        return x_c, y_c

    def _set_segment(self, x_top_left:int, y_top_left: int, x_bottom_right: int, y_bottom_right: int):
        if x_top_left >= x_bottom_right or y_top_left >= y_bottom_right:
            raise PositionException(x_top_left, y_top_left, x_bottom_right, y_bottom_right)
        for cord in [x_top_left, y_top_left, x_bottom_right, y_bottom_right]:
            if type(cord) is float:
                raise TypeArgError(x_top_left, y_top_left, x_bottom_right, y_bottom_right)    
        self.x_top_left = x_top_left
        self.y_top_left = y_top_left
        self.x_bottom_right = x_bottom_right
        self.y_bottom_right = y_bottom_right


    def set_segment_2p(self, dict_2point: Dict):
        self._set_segment(dict_2point["x_top_left"], dict_2point["y_top_left"], 
                          dict_2point["x_bottom_right"], dict_2point["y_bottom_right"])
        

    def set_segment_p_size(self, dict_2point: Dict):
        self._set_segment(dict_2point["x_top_left"], dict_2point["y_top_left"], 
                          dict_2point["width"] + dict_2point["x_top_left"],
                          dict_2point["height"] + dict_2point["y_top_left"])
    

    def set_segment_max_segments(self, segments: List["ImageSegment"]):
        list_x_top_left = [segment.x_top_left for segment in segments]
        list_y_top_left = [segment.y_top_left for segment in segments]
        list_x_bottom_right = [segment.x_bottom_right for segment in segments]
        list_y_bottom_right = [segment.y_bottom_right for segment in segments]
        self.x_top_left = min(list_x_top_left)
        self.y_top_left = min(list_y_top_left)
        self.x_bottom_right = max(list_x_bottom_right)
        self.y_bottom_right = max(list_y_bottom_right)


    def add_info(self, key:str, val:np.ndarray):
        self.info[key] = val

    def get_info(self, key):
        return self.info[key]
    
    def is_intersection(self, seg):
        points1 = [(seg.x_top_left, seg.y_top_left),
                   (seg.x_top_left, seg.y_bottom_right),
                   (seg.x_bottom_right, seg.y_top_left),
                   (seg.x_bottom_right, seg.y_bottom_right),
                   seg.get_center()]

        points2 = [(self.x_top_left, self.y_top_left),
                   (self.x_top_left, self.y_bottom_right),
                   (self.x_bottom_right, self.y_top_left),
                   (self.x_bottom_right, self.y_bottom_right),
                   self.get_center()]

        for p in points1:
            if (self.x_top_left < p[0]) and (self.x_bottom_right > p[0]) and \
                    (self.y_top_left < p[1]) and (self.y_bottom_right > p[1]):
                return True
        for p in points2:
            if (seg.x_top_left < p[0]) and (seg.x_bottom_right > p[0]) and \
                    (seg.y_top_left < p[1]) and (seg.y_bottom_right > p[1]):
                return True
        
        return False

    def add_segment(self, seg):
        c2 = seg.get_segment_2p()
        self.set_segment_2p({
            "x_top_left": min(self.x_top_left, c2["x_top_left"]),
            "x_bottom_right": max(self.x_bottom_right, c2["x_bottom_right"]),
            "y_top_left": min(self.y_top_left, c2["y_top_left"]),
            "y_bottom_right": max(self.y_bottom_right, c2["y_bottom_right"]),
        })


    def get_min_dist(self, seg: "ImageSegment"):
        x_right = seg.x_top_left-self.x_bottom_right
        x_left = self.x_top_left-seg.x_bottom_right 
        y_bottom = seg.y_top_left-self.y_bottom_right
        y_top = self.y_top_left-seg.y_bottom_right

        
        dist = [
            [x_right,y_bottom], 
            [x_left,y_bottom], 
            [x_right,y_top],
            [x_left,y_top]
        ]

        array_d = [
            x_right**2 + y_bottom**2,
            x_left**2 + y_bottom**2,
            x_right**2 + y_top**2,
            x_left**2 + y_top**2
        ]

        i = np.argmin(array_d)
        
        return array_d[i]**0.5 if dist[i][0]*dist[i][1] > 0 else max(dist[i])


    def get_angle_center(self, seg: "ImageSegment"):
        # abs(cos x)
        x1, y1 = self.get_center() 
        x2, y2 = seg.get_center() 
        den = ((y1-y2)**2 + (x1-x2)**2)**0.5
        num = abs(x1-x2)
        return num/den if den != 0 else 0.0
        

    def plot(self, color="b", text="", width=1):
        x0 = self.x_top_left
        y0 = self.y_top_left
        x1 = self.x_bottom_right
        y1 = self.y_bottom_right
        plt.plot([x0, x0, x1, x1, x0], [y0, y1, y1, y0, y0], color=color, linewidth=width)
        plt.text(x=x0, y=y0, s=text)

    def resize(self, k):
        self.x_top_left = round(k*self.x_top_left)
        self.y_top_left = round(k*self.y_top_left)
        self.x_bottom_right = round(k*self.x_bottom_right)
        self.y_bottom_right = round(k*self.y_bottom_right)


class SegmentException(Exception):
    def __init__(self, x_top_left, y_top_left, x_bottom_right, y_bottom_right):
        self.x_top_left = x_top_left
        self.x_bottom_right = x_bottom_right
        self.y_top_left = y_top_left
        self.y_bottom_right = y_bottom_right

class PositionException(SegmentException):
    def __str__(self):
        return f"\nx_top_left = {self.x_top_left} < x_bottom_right = {self.x_bottom_right}\n" \
               f"y_top_left = {self.y_top_left} < y_bottom_right = {self.y_bottom_right}\n"
    
class TypeArgError(SegmentException):
    def __str__(self):
        str_ = ""
        if type(self.x_top_left) is not int:
            str_ += f"x_top_left - {type(self.x_top_left)}\n"
        if type(self.x_bottom_right) is not int:
            str_ += f"x_bottom_right - {type(self.x_bottom_right)}\n"
        if type(self.y_top_left) is not int:
            str_ += f"y_top_left - {type(self.y_top_left)}\n"
        if type(self.y_bottom_right) is not int:
            str_ += f"x_top_left - {type(self.y_bottom_right)}\n"
        return str_
 