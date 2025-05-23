from ...base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from typing import Dict, List
from ...dtype import Word
from ..segment_clusterizer import KMeanClusterizer
import numpy as np
import matplotlib.pyplot as plt

class SpGraph4NModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.A = None
        self.nodes_feature  = None
        self.edges_feature = None
        self.true_edges = None
        self.true_nodes = None

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"A": self.A.tolist(), "nodes_feature":self.nodes_feature.tolist(), "edges_feature": self.edges_feature.tolist()}

    def read_from_file(self, path_file: str) -> None:
        pass

    def clean_model(self):
        self.A = None
        self.nodes_feature  = None
        self.edges_feature = None

    def show(self):
        def get_color(i):
            if i == -1:
                return "black"
            elif i == 0:
                return "aqua"
            elif i == 1:
                return "gold"
            elif i == 2:
                return "lime"
            elif i == 3:
                return "violet"
            elif i == 4:
                return "teal"
            
        def plot_index(indexs, colors=["b", "b", "r"]):
            i, j = indexs
            #TODO: автоматически подтянуть длину вектора
            xi = self.nodes_feature[i][32]
            yi = self.nodes_feature[i][33]
            xj = self.nodes_feature[j][32]
            yj = self.nodes_feature[j][33]
            plt.scatter(xi, yi, c=colors[0])
            plt.scatter(xj, yj, c=colors[1])
            plt.plot([xi, xj], [yi, yj], colors[2])
        if self.true_edges is None:
            for indexs in zip(self.A[0], self.A[1]):
                plot_index(indexs)
        else:
            for k, indexs in enumerate(zip(self.A[0], self.A[1] )):
                i, j = indexs
                plot_index(indexs, [get_color(self.true_nodes[i]), 
                                    get_color(self.true_nodes[j]), "g" if self.true_edges[k] == 1 else "r"])


class WordsToSpGraph4N(BaseConverter):
    def __init__(self) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()


    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        words = input_model.words
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
        output_model.nodes_feature = np.array([w.segment.get_height() for w in words])
        output_model.edges_feature = np.array(edges_feature)

class Graph4NModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.words: List[Word] = []
        self.Y = None
        self.X = None
        self.graph4n = None
        self.sparce_graph = None

    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"neighbors": self.graph4n, "edges":self.sparce_graph, "words": [w.to_dict() for w in self.words]}

    def read_from_file(self, path_file: str) -> None:
        pass

    def clean_model(self):
        self.blocks = []
    
class WordsToGraph4N(BaseConverter):
    def __init__(self) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()


    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        output_model.words = input_model.words
        output_model.graph4n = self.kmean_clusterizer.get_index_neighbors_segment([w.segment for w in output_model.words])
        edges = [[], []]
        for i, nodes in enumerate(output_model.graph4n):
            for j in nodes:
                if not (i in edges[1] and j in edges[0]): # i-j еще нет, проверка что нет j-i
                    edges[0].append(i)
                    edges[1].append(j)
        output_model.X = []
        output_model.sparce_graph = edges

class PhisicalToGraph4N(WordsToGraph4N):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        hash = []
        words = []
        hash_index = 0
        for block in input_model.blocks:
            for w in block.words:
                words.append(w)
                hash.append(hash_index)
            hash_index += 1

        output_model.words = words
        output_model.graph4n = self.kmean_clusterizer.get_index_neighbors_segment([w.segment for w in output_model.words])
        edges = [[], [], []]

        class_nodes = [0 for _ in words]
        for i, nodes in enumerate(output_model.graph4n):
            for j in nodes:
                if not (i in edges[1] and j in edges[0]): # i-j еще нет, проверка что нет j-i
                    edges[0].append(i)
                    edges[1].append(j)
                    
                    if hash[i]-hash[j] != 0: # если хотя бы один сосед не из того блока, то это граница
                        class_nodes[i] = 1
                        edges[2].append(0)
                    else:
                        edges[2].append(1)
        output_model.X = []
        output_model.Y = class_nodes
        output_model.sparce_graph = edges


#EXTRACTORS ===================================================================

class AngExtractor(BaseExtractor):
    def extract(self, model: BaseSubModel) -> None:
        nodes = [w.segment.get_center() for w in model.words]
        angs = [self.cos(nodes[i], nodes[j]) for i, j in zip(model.sparce_graph[0], model.sparce_graph[1])]
        model.sparce_graph.append(angs)
    
    def cos(self, n1, n2):
        dx = (n1[0]-n2[0])
        dy = (n1[1]-n2[1])
        dt = (dx**2+dy**2)**0.5
        return abs(dx)/dt if dt != 0 else 0
    
class DistExtractor(BaseExtractor):
    def extract(self, model: BaseSubModel) -> None:
        nodes = [w.segment.get_center() for w in model.words]
        dist = [self.dist(nodes[i], nodes[j]) for i, j in zip(model.sparce_graph[0], model.sparce_graph[1])]
        dist_max = max(dist)
        dist = [d/dist_max for d in dist]
        model.sparce_graph.append(dist)
    
    def dist(self, n1, n2):
        dx = (n1[0]-n2[0])
        dy = (n1[1]-n2[1])
        dt = (dx**2+dy**2)**0.5
        return dt
    
class NodeAngExtractot(AngExtractor):
    def extract(self, model: BaseSubModel) -> None:
        nodes = [w.segment.get_center() for w in model.words]
        
        angs = [[self.cos(nodes[i], nodes[j]) for j in n ] for i, n in enumerate(model.graph4n) ]
        angs_min = [np.min(a) for a in angs]
        angs_max = [np.max(a) for a in angs]
        angs_mean = [np.mean(a) for a in angs]
        model.X.append(angs_min)
        model.X.append(angs_max)
        model.X.append(angs_mean)

class NodeDistExtractot(DistExtractor):
    def extract(self, model: BaseSubModel) -> None:
        nodes = [w.segment.get_center() for w in model.words]
        
        dist = [[self.dist(nodes[i], nodes[j]) for j in n ] for i, n in enumerate(model.graph4n) ]
        dist_max = np.max(dist)
        dist_max = dist_max if dist_max != 0 else 1
        dist = [[di/dist_max for di in d] for d in dist]
        dist_min = [np.min(a) for a in dist]
        dist_max = [np.max(a) for a in dist]
        dist_mean = [np.mean(a) for a in dist]
        model.X.append(dist_min)
        model.X.append(dist_max)
        model.X.append(dist_mean)
