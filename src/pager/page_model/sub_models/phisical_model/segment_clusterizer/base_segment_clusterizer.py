from abc import ABC, abstractmethod
from pager.page_model.sub_models.dtype import ImageSegment
from typing import List, Dict


class BaseSegmentClusterizer(ABC):
    @abstractmethod
    def cluster(self, segments: List[ImageSegment], conf: Dict) -> List[ImageSegment]:
        pass

    def join_intersect_segments(self, segments: List[ImageSegment]) -> List[ImageSegment]:
        new_segments = segments
        run = True
        while run:
            old_segments = new_segments
            new_segments = []
            for seg in old_segments:
                self.__add_block_in_new_list(new_segments, seg)
            if len(new_segments) == len(old_segments):
                run = False
        return new_segments


    def __add_block_in_new_list(self, new_segments, seg):
        for new_segment in new_segments:
            if new_segment.is_intersection(seg):
                new_segment.add_segment(seg)
                return
        new_segments.append(seg)
