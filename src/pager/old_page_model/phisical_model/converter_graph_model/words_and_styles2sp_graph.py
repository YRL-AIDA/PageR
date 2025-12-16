from ...base_sub_model import BaseSubModel, BaseConverter
from ..segment_clusterizer import KMeanClusterizer, DelaunayClusterizer
import numpy as np
from typing import Dict, List
from transformers import BertTokenizer, BertModel
import torch
from ...dtype import ImageSegment
import os
from pager.nn_models.sys_model_manager import get_model_path
from pager import device

SIZE_VEC = 32
BERT_COUNT_WORD_AT_ONCE= 250
PATH_MODELS = get_model_path('bert')

class Word2Vec():
    def __init__(self):
        model_dir = os.path.join(PATH_MODELS, 'models--bert-base-multilingual-cased',
                             'snapshots','3f076fdb1ab68d5b2880cb87a0886f315b8146f8')
        self.tokenizer = BertTokenizer.from_pretrained(model_dir)
        self.model = BertModel.from_pretrained(model_dir).to(device)
    
    def __call__(self, words):
        if len(words) == 0:
            return np.array([[]])
        k = len(words)//BERT_COUNT_WORD_AT_ONCE
        over = len(words)%BERT_COUNT_WORD_AT_ONCE
        output_array = np.zeros((len(words), SIZE_VEC))
        for i in range(0, k):
            a = i*BERT_COUNT_WORD_AT_ONCE
            b = (i+1)*BERT_COUNT_WORD_AT_ONCE
            part_words = words[a:b]
            inputs = self.tokenizer(part_words, return_tensors="pt", padding=True).to(device)
            outputs = self.model(**inputs)
            output_array[a:b] = outputs.last_hidden_state.mean(dim=1).detach().cpu().numpy()[:, :SIZE_VEC]
        if over != 0:
            part_words = words[-over:]
            inputs = self.tokenizer(part_words, return_tensors="pt", padding=True).to(device)
            outputs = self.model(**inputs)
            output_array[-over:] = outputs.last_hidden_state.mean(dim=1).detach().cpu().numpy()[:, :SIZE_VEC]
        return output_array

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
    def __init__(self, conf=None, add_text=True) -> None:
        super().__init__()
        self.kmean_clusterizer = KMeanClusterizer()
        self.with_text = False
        self.add_text = add_text
        if conf is not None:
            self.with_text = conf["with_text"] if "with_text" in conf.keys() else False


    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        words= input_model.words
        styles = input_model.styles
        segments: List[ImageSegment]  = [w.segment for w in words]
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

        if self.add_text:
            output_model.nodes_feature = np.array(self.get_vec_words(words, styles, self.with_text))
            output_model.edges_feature = np.array(edges_feature)
        else:
            output_model.nodes_feature = np.array([]) #np.array(self.get_vec_words(words, styles, self.with_text))
            output_model.edges_feature = np.array([]) #np.array(edges_feature)
    
class WordsAndStylesToSpDelaunayGraph(WordsAndStylesToSpG):
    def __init__(self, conf=None, add_text=True) -> None:
        super().__init__()
        self.delaunay_clusterizer = DelaunayClusterizer()
        self.with_text = False
        self.add_text = add_text
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
        #TODO: TEST !!!!

        if self.add_text:
            output_model.nodes_feature = np.array(self.get_vec_words(words, styles, self.with_text))
            output_model.edges_feature = np.array(edges_feature)
        else:
            output_model.nodes_feature = np.array([]) #np.array(self.get_vec_words(words, styles, self.with_text))
            output_model.edges_feature = np.array([]) #np.array(edges_feature)
