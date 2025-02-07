from ...base_sub_model import BaseSubModel, BaseConverter
from ..segment_clusterizer import KMeanClusterizer, DelaunayClusterizer
import numpy as np
from typing import Dict
from transformers import BertTokenizer, BertModel
import torch

SIZE_VEC = 32
class Word2Vec():
    def __init__(self):
        model_name = "bert-base-multilingual-cased"  # Многоязычная модель BERT
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
    
    def __call__(self, words):
        if len(words) == 0:
            return np.array([[]])
        inputs = self.tokenizer(words, return_tensors="pt", padding=True)
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()[:, :SIZE_VEC]

class WordsAndStylesToSpG(BaseConverter):
    def __init__(self) -> None:
        super().__init__()
        self.word2vec = Word2Vec()
    
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        pass

    def _get_vec_styles_word(self, w, styles):
        style = [s for s in styles if s.id == w.style_id][0]
        vec = style.to_dict(is_vec=True)["font2vec"]
        x, y = w.segment.get_center()
        return [x, y, *vec]
    
    def get_vec_words(self, words, styles, with_text=False):
        styles_vec = [self._get_vec_styles_word(w, styles) for w in words] if len(words) != 0 else np.array([[]])
        if not with_text:
            return styles_vec
        text_vec = self.word2vec([ w.content for w in words])
        return np.concatenate((text_vec, styles_vec), axis=1)


class WordsAndStylesToSpGraph4N(WordsAndStylesToSpG):
    def __init__(self, conf=None) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()
        self.with_text = False
        if conf is not None:
            self.with_text = conf["with_text"] if "with_text" in conf.keys() else False


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
        output_model.nodes_feature = np.array(self.get_vec_words(words, styles, self.with_text))
        output_model.edges_feature = np.array(edges_feature)
    
class WordsAndStylesToSpDelaunayGraph(WordsAndStylesToSpG):
    def __init__(self, conf=None) -> None:
        super().__init__()
        self.delaunay_clusterizer = DelaunayClusterizer()
        self.with_text = False
        if conf is not None:
            self.with_text = conf["with_text"] if "with_text" in conf.keys() else False

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
        output_model.nodes_feature = np.array(self.get_vec_words(words, styles, self.with_text))
        output_model.edges_feature = np.array(edges_feature)
