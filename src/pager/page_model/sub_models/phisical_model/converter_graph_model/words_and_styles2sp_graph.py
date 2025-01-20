from ...base_sub_model import BaseSubModel, BaseConverter
from ..segment_clusterizer import KMeanClusterizer, DelaunayClusterizer
import numpy as np

class WordsAndStylesToSpG(BaseConverter):
    def __init__(self) -> None:
        super().__init__()
    
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        pass

    def get_vec_word(self, w, styles):
        style = [s for s in styles if s.id == w.style_id][0]
        vec = style.to_dict(is_vec=True)["font2vec"]
        x, y = w.segment.get_center()
        return [x, y, *vec]


class WordsAndStylesToSpGraph4N(WordsAndStylesToSpG):
    def __init__(self) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()


    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        words = input_model.words
        styles = input_model.styles
        segments = [w.segment for w in words]
        graph4n = self.kmean_clusterizer.get_index_neighbors_segment(segments)
        distans = self.kmean_clusterizer.get_distans(graph4n, segments)
        edges = [[], []]
        edges_feature = []
        for i, nodes in enumerate(graph4n):
            for k, j in enumerate(nodes):
                if not (i in edges[1] and j in edges[0]): # i-j еще нет, проверка что нет j-i
                    edges[0].append(i)
                    edges[1].append(j)
                    edges_feature.append(distans[i][k])
        output_model.A = np.array(edges)
        output_model.nodes_feature = np.array([self.get_vec_word(w, styles) for w in words])
        output_model.edges_feature = np.array(edges_feature)
    
class WordsAndStylesToSpDelaunayGraph(WordsAndStylesToSpG):
    def __init__(self) -> None:
        super().__init__()
        self.delaunay_clusterizer = DelaunayClusterizer()

    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        words = input_model.words
        styles = input_model.styles
        segments = [w.segment for w in words]
        A, distans = self.delaunay_clusterizer.get_A_and_distans(segments)
        edges = [[], []]
        edges_feature = []
        for i, row in enumerate(A):
            for j, a in enumerate(row):
                if a != 0 : # i-j еще нет, проверка что нет j-i
                    edges[0].append(i)
                    edges[1].append(j)
                    edges_feature.append(distans[i][j])
        output_model.A = np.array(edges)
        output_model.nodes_feature = np.array([self.get_vec_word(w, styles) for w in words])
        output_model.edges_feature = np.array(edges_feature)