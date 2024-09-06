import unittest
import numpy as np
from pager import ImageModel

class TestImage(unittest.TestCase):
    img_model=ImageModel()

    def test_size(self) -> None:
        self.img_model.read_from_file('files/6p.png')
        shape = self.img_model.img.shape
        self.assertEqual(shape[0],3)
        self.assertEqual(shape[1],2)
        self.assertEqual(shape[2],3)

    def test_color_RGB(self) -> None:
        self.img_model.read_from_file('files/6p.png')
        img = self.img_model.img
        
        RED = np.array([255, 0, 0])
        GREEN = np.array([0, 255, 0])
        BLUE = np.array([0, 0, 255])
        BLACK = np.array([0, 0, 0])
        WHITE = np.array([255, 255, 255])
        BROWN = np.array([150, 100, 50])

        list_color= [[WHITE, BLACK], [RED, GREEN], [BLUE, BROWN]]
        for i in range(3):
            for j in range(2):
                self.assertEqual(np.sum((list_color[i][j] - img[i, j])**2), 0, f'ERROR in px<{i}, {j}>')
        


