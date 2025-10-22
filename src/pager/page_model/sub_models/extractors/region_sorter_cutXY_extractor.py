# https://github.com/YRL-AIDA/ReadingOrderDetection/tree/main/dtype/sorters/layout_XYCut

from ..base_sub_model import BaseExtractor
from ..region_model import RegionModel
from ..dtype.image_segment import ImageSegment

class Walley:
    '''
    Класс который нужен для раздлеления блоков на группы, в завимости от их расположения относительно разделений.

    '''
    id = 0

    def __init__(self, bboxes:list[ImageSegment] = None):
        self.id = Walley.id
        Walley.id += 1

        if bboxes is None: 
            self.bboxes = []
        else:
            self.bboxes = bboxes


    @staticmethod
    def get_max_min(bboxes: list[ImageSegment]):
        min_x = min([bbox.x_top_left for bbox in bboxes])
        min_y = min([bbox.y_top_left for bbox in bboxes])
        max_x = max([bbox.x_bottom_right for bbox in bboxes])
        max_y = max([bbox.y_bottom_right for bbox in bboxes])

        return (min_x, min_y), (max_x, max_y)
    def __repr__(self):
        return f"id:{self.id}, {self.bboxes}, минимальные и максимальные координаты: {Walley.get_max_min(self.bboxes)}"
    
class Edge:
    '''
    Узел, нужен для составления дерева
    '''
    id = 0
    def __init__(self, number, childs:list['Edge'] = None):
        self.id = Edge.id
        Edge.id += 1

        self.number = number
        if childs is None: 
            self.childs = []
        else:
            self.childs = childs

    def __repr__(self):
        return f"Узел id:{self.id}, number = {self.number}"
    

class RegionSorterCutXYExtractor(BaseExtractor):
    def extract(self, model:RegionModel):
        bboxes = [reg.segment for reg in model.regions]
        for i, bbox in enumerate(bboxes):
            bbox.id = i
        order = self.sort_using_XYCut(bboxes)
        model.set_regions([model.regions[i] for i in order])


    def sort_using_XYCut(self, bboxes) -> list[int]:
        
        init_edge = Edge(number = "init")
        init_walley = Walley(bboxes=bboxes)
        RegionSorterCutXYExtractor.reqursion_step(walley=init_walley, edge=init_edge)
        res = []
        def print_childs(childsd):
            for child in childsd:
                if child.number == -1:
                    print_childs(child.childs)
                else:
                    res.append(child.number)
        print_childs(init_edge.childs)
        return res


    @staticmethod
    def reqursion_step(walley: Walley, edge:Edge) -> list[Edge]:
        '''
        Шаг рекурсии, возвращает массив эджей, который представляет собой детей родительского эджа.
        '''
        bboxes = walley.bboxes
        min_coor, max_coor = Walley.get_max_min(bboxes)
        proec_x = RegionSorterCutXYExtractor._proection_x(bboxes, min_coor, max_coor)
        proec_y = RegionSorterCutXYExtractor._proection_y(bboxes, min_coor, max_coor)

        if proec_x:
            RegionSorterCutXYExtractor._get_childs_x(bboxes, proec_x, min_coor, max_coor, edge=edge)
        elif proec_y:
            RegionSorterCutXYExtractor._get_childs_y(bboxes, proec_y, min_coor, max_coor, edge=edge)
        else:
            grups = [Edge(number=bbox.id) for bbox in bboxes]
            # print(grups, "Если не произошло разделения")
            return grups

    @staticmethod
    def _get_childs_x(bboxes:list[ImageSegment], proec_x, min_coor, max_coor, edge:Edge):
        steps = [min_coor[0]] + proec_x + [max_coor[0]]
        grups = []
        for _ in range(len(proec_x) + 1):
            grups.append(Walley())

        for i, (first, second) in enumerate(zip(steps[:-1], steps[1:])):
            for bbox in bboxes:
                if first <= bbox.x_top_left <= second: #Расчет на то что если левый угол ббокса в группе проекционной, то и правая тоже
                    grups[i].bboxes.append(bbox)

        result = []
        for walley in grups:
            if len(walley.bboxes) <= 1:
                result.append(Edge(walley.bboxes[0].id))
            else:
                temp = Edge(number=-1)
                RegionSorterCutXYExtractor.reqursion_step(walley, edge=temp)
                result.append(temp)
        edge.childs = result


    @staticmethod
    def _get_childs_y(bboxes:list[ImageSegment], proec_y, min_coor, max_coor, edge:Edge):
        steps = [min_coor[1]] + proec_y + [max_coor[1]]
        grups = []
        for _ in range(len(proec_y) + 1):
            grups.append(Walley())

        for i, (first, second) in enumerate(zip(steps[:-1], steps[1:])):
            for bbox in bboxes:
                if first <= bbox.y_top_left <= second: #Расчет на то что если левый угол ббокса в группе проекционной, то и правая тоже
                    grups[i].bboxes.append(bbox)
        result = []
        for walley in grups:
            if len(walley.bboxes) <= 1:

                result.append(Edge(walley.bboxes[0].id))
            else:
                temp = Edge(number=-1)
                RegionSorterCutXYExtractor.reqursion_step(walley, edge=temp)
                result.append(temp)
        edge.childs = result


    @staticmethod
    def _proection_x(bboxes:list[ImageSegment], min_ccor, max_coor):
        proections = []
        flag = 1
        for x in range(min_ccor[0], max_coor[0], 1): #шаг тут конечно под вопросом какой ставить
            count = 0
            for bbox in bboxes:
                if bbox.x_top_left <= x < bbox.x_bottom_right:
                    count += 1
            if count == 0:
                if len(proections)!=0:
                    if x != (proections[-1] + 1) and flag == 1:
                        proections.append(x)
                        break
                        flag = 0
                else:
                    flag = 0
                    
                    proections.append(x)
                    break
            else:
                flag = 1
        return proections if len(proections) != 0 else False


    @staticmethod
    def _proection_y(bboxes:list[ImageSegment], min_ccor, max_coor):
        proections = []
        flag = 1
        for y in range(min_ccor[1], max_coor[1], 1): #шаг тут конечно под вопросом какой ставить
            count = 0
            for bbox in bboxes:
                if bbox.y_top_left <= y < bbox.y_bottom_right:
                    count += 1

            if count == 0:
                if len(proections)!=0:
                    if y != (proections[-1] + 1) and flag == 1:
                        flag = 0
                        proections.append(y)
                        break
                else:
                    proections.append(y)
                    break
                    flag = 0
            else:
                flag = 1
        return proections if len(proections) != 0 else False
    

