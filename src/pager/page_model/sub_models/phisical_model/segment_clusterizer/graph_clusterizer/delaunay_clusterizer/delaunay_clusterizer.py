import numpy as np
from ..base_graph_clusterizer import *

from pager.page_model.sub_models.dtype import ImageSegment
from pager.page_model.sub_models.dtype  import Graph
import numpy as np
from typing import Dict, List
from scipy.spatial import Delaunay


class DelaunayClusterizer(BaseSegmentClusterizer):
    def cluster(self, segments: List[ImageSegment], conf: Dict={}) -> List[ImageSegment]:
        A, distans = self.get_A_and_distans(segments)
        graph = self.get_graph_segments(segments, distans)
        parent_segments = []
        for r in graph.get_related_graphs():
            seg = ImageSegment(0, 0, 1, 1)
            segment_r = [segments[n.index-1] for n in r.get_nodes()]
            seg.set_segment_max_segments(segment_r)
            parent_segments.append(seg)
        join_intersect_parent_segments = self.join_intersect_segments(parent_segments)
        return join_intersect_parent_segments

    def get_A_and_distans(self, segments):
        points = np.array([seg.get_center() for seg in segments])
        tri = Delaunay(points)
        
        N = len(points)
        A = np.zeros((N, N))
        E = np.zeros((N, N))
        for t in tri.simplices:
            e1 = segments[t[0]].get_min_dist(segments[t[1]])
            e2 = segments[t[2]].get_min_dist(segments[t[1]])
            e3 = segments[t[0]].get_min_dist(segments[t[2]])
            A[t[0], t[1]] = 1
            A[t[1], t[0]] = 1
            E[t[0], t[1]] = e1
            E[t[1], t[0]] = e1
            
            A[t[2], t[1]] = 1
            A[t[1], t[2]] = 1
            E[t[2], t[1]] = e2
            E[t[1], t[2]] = e2
        
            
            A[t[0], t[2]] = 1
            A[t[2], t[0]] = 1
            E[t[0], t[2]] = e3
            E[t[2], t[0]] = e3
        return A, E
        
    def get_graph(self, segments, distans):
        graph = Graph()
        for seg in segments:
            c1x, c1y = seg.get_center()
            index = graph.add_node(c1x, c1y) # seg_index + 1

        m = np.mean(distans)
        std = np.std(distans)
        for i, row in enumerate(edges):
            for j, d in enumerate(row[i:]):
                if d >= m-2*std:
                    graph.add_edge(i+1, j+1)
        return graph
                    
