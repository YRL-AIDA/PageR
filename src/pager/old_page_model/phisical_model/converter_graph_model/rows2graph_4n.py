from pager.page_model.sub_models.phisical_model.segment_clusterizer import KMeanClusterizer
from ...base_sub_model import BaseSubModel, BaseConverter
from typing import List
from ...dtype import ImageSegment

import numpy as np

class RowToSpGraph4N(BaseConverter):
    def __init__(self, conf=None, add_text=True) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()
        self.with_text = False
        self.add_text = add_text
        if conf is not None:
            self.with_text = conf["with_text"] if "with_text" in conf.keys() else False
        
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        rows = input_model.rows
        segments: List[ImageSegment]  = [r.segment for r in rows]
        graph4n = self.kmean_clusterizer.get_index_neighbors_segment(segments)
        distans = self.kmean_clusterizer.get_distans(graph4n, segments)
        edges_set = set()
        edges = [[], []]
        edges_feature = []
        for i, nodes in enumerate(graph4n):
            for k, j in enumerate(nodes):
                edge = (min(i, j), max(i, j))
                if edge in edges_set:
                    continue
                edges_set.add(edge)
                
                edges[0].append(i)
                edges[1].append(j)
                edges_feature.append([
                    distans[i][k],
                    segments[i].get_angle_center(segments[j]),
                    ])
        output_model.A = np.array(edges)
        #TODO: TEST !!!!

        # if self.add_text:
        #     output_model.nodes_feature = np.array(self.get_vec_words(words, styles, self.with_text))
        #     output_model.edges_feature = np.array(edges_feature)
        # else:
        output_model.nodes_feature = np.array([]) #np.array(self.get_vec_words(words, styles, self.with_text))
        output_model.edges_feature = np.array([]) #np.array(edges_feature)
    