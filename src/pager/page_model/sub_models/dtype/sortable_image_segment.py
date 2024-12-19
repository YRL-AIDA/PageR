from .image_segment import ImageSegment

class Top2BottomLeft2RightImageSegment(ImageSegment):
    
    def __init__(self, x_top_left: int, y_top_left: int, x_bottom_right: int, y_bottom_right: int) -> None:
        super().__init__(x_top_left, y_top_left, x_bottom_right, y_bottom_right)
        
    
    @staticmethod
    def converter(seg: ImageSegment):        
        return Top2BottomLeft2RightImageSegment(seg.x_top_left, seg.y_top_left, seg.x_bottom_right, seg.y_bottom_right)
        
    def eps(self, seg: "Top2BottomLeft2RightImageSegment"):
        eps = max(self.get_height(), seg.get_height())
        return eps
    
    def __gt__(self, seg: "Top2BottomLeft2RightImageSegment"):
        eps = self.eps(seg)
        if self.y_top_left> seg.y_top_left + eps:
            return True
        elif abs(seg.y_top_left - self.y_top_left) < eps and self.x_top_left < seg.x_top_left:
            return True
        return False
    
    def __lt__(self, seg: 'Top2BottomLeft2RightImageSegment'):
        eps = self.eps(seg)
        if self.y_top_left  + eps < seg.y_top_left:
            return True
        elif abs(seg.y_top_left - self.y_top_left) < eps and seg.x_top_left > self.x_top_left:
            return True
        return False
    
    def point_is_in_bbox(self, point : list) -> bool:
        x = point[0]
        y = point[1]
        
        return (x >= self.x_top_left and x <= self.x_bottom_right and y >= self.y_top_left and y <= self.y_bottom_right)