from .torch_segmodel_utils import get_segmenter as get_models_seg, torch_classification_edges 
from .glam_model import load_weigths, NodeGLAM, EdgeGLAM, get_tensor_from_graph

from ..converter_graph_model import SpGraph4NModel, WordsAndStylesToSpGraph4N
from ...base_sub_model import BaseSubModel, BaseConverter
from typing import Dict, List
from ...dtype import ImageSegment, Block, Graph, Word
import os
import torch
import numpy as np
from dotenv import load_dotenv
load_dotenv()

class EdgeSegNodeClassConverter(BaseConverter):
    def __init__(self, conf:Dict = {}) -> None:
        self.spgraph = SpGraph4NModel()
        self.name_class = ["no_struct", "text", "header", "list", "table"]
        self.converter = conf['graph_converter'] if "graph_converter" in conf.keys() else  WordsAndStylesToSpGraph4N()
    
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        words = input_model.words        
        self.converter.convert(input_model, self.spgraph)
        graph = self.spgraph.to_dict()
        self.set_output_block(output_model, words, graph)
    
    
    def set_output_block(self, output_model, words, graph):
        # SEGMENTER ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        edges_ind = self.segmenter(graph)
        relating_graph = Graph()
        for word in words:
            x, y = word.segment.get_center()
            relating_graph.add_node(x, y)
        
        for n1, n2, ind in zip(graph['A'][0], graph['A'][1], edges_ind):
            if ind == 1:
                relating_graph.add_edge(n1+1, n2+1)

        for r in relating_graph.get_related_graphs():
            words_r = [words[n.index-1] for n in r.get_nodes()]
            segment = ImageSegment(0, 0, 1, 1)
            segment.set_segment_max_segments([word.segment for word in words_r])
            block = Block(segment.get_segment_2p())
            
            #TODO: Решить проблему с типами в блоке
            words_ = [word.to_dict()['segment'] for word in words_r]
            for word_, word in zip(words_, words_r):
                word_["text"] = word.content
            #TODO: Нужно сделать, чтоб перебирались все варианты, пока ни разу не зайдет
            skip = False
            for old_block in output_model.blocks:
                if old_block.segment.is_intersection(block.segment):
                    old_block.segment.set_segment_max_segments([old_block.segment, block.segment])
                    old_block.words += [Word(w) for w in words_]
                    old_block.sort_words()
                    skip = True
            if skip:
                continue
            block.set_words_from_dict(words_)
            block.sort_words()
            output_model.blocks.append(block)
        
        self.set_label_output_block(output_model, words, graph)
        
    def set_label_output_block(self, output_model, words, graph):
        # CLASSIFIER +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        subgraphs = []
        for block in output_model.blocks:
            subgraph = {
                "A": [[], []],
                "nodes_feature": [],
                "edges_feature": [],
            }

            block_nodes = []
            for i, word in enumerate(words):
                if block.segment.is_intersection(word.segment):
                    block_nodes.append(i)
                    subgraph["nodes_feature"].append(graph["nodes_feature"][i])

            for i, (n1, n2) in enumerate(zip(graph["A"][0], graph["A"][1])):
                if n1 in block_nodes and n2 in block_nodes:
                    subgraph["A"][0].append(block_nodes.index(n1))
                    subgraph["A"][1].append(block_nodes.index(n2))
                    subgraph["edges_feature"].append(graph["edges_feature"][i])

            subgraphs.append(subgraph) 
        for block, sg in zip(output_model.blocks, subgraphs):
            class_ = self.classifier(sg)
            # class_ = 1
            label = self.name_class[class_]
            block.set_label(label)

    def segmenter(self, graph) -> List[int]:
        pass

    def classifier(self, graph) -> int:
        pass
        



class WordsAndStylesToGNNpLinearBlocks(EdgeSegNodeClassConverter):
    def __init__(self, conf:Dict = {}) -> None:
        super().__init__(conf)
        params = {
            "count_neuron_layers_gnn": [9, 27, 18],
            "count_neuron_layers_edge": [18*2, 1],
            "path_node_gnn": conf["path_node_gnn"],
            "path_edge_linear": conf["path_edge_linear"]
        }
        self.seg_k = conf['seg_k'] if "seg_k" in conf.keys() else 0.5
        self.model_seg = get_models_seg(params)

    def segmenter(self, graph) -> List[int]:
        return torch_classification_edges(self.model_seg, graph, self.seg_k)
    
    def classifier(self, graph) -> int:
        return 1


class WordsAndStylesToGLAMBlocks(EdgeSegNodeClassConverter):
    def __init__(self, conf):
        super().__init__(conf)
        params = {
            "H1": conf["H1"],
            "H2": conf["H2"],
            "node_featch": conf["node_featch"],
            "edge_featch": conf["edge_featch"],
            "path_node_gnn": conf["path_node_gnn"],
            "path_edge_linear": conf["path_edge_linear"]
        }
        self.seg_k = conf['seg_k'] if "seg_k" in conf.keys() else 0.5
        self.spgraph = SpGraph4NModel()
        self.graph_converter = WordsAndStylesToSpGraph4N({"with_text": True})
        
        self.name_class = ["figure", "text", "header", "list", "table"]
        models = [NodeGLAM(params["node_featch"], params["H1"], 5), 
                  EdgeGLAM(2*params["node_featch"]+2*5+params["edge_featch"], params["H2"], 1)]
        self.models = load_weigths(models, conf["path_node_gnn"], conf["path_edge_linear"])
    
    def convert(self, input_model, output_model)-> None:
        words = input_model.words   
        self.graph_converter.convert(input_model, self.spgraph)
        graph = self.spgraph.to_dict()
        self.set_output_block(output_model, words, graph)
            
    def segmenter(self, graph) -> List[int]:
        X, Y, sp_A, i = get_tensor_from_graph(graph)
        N = X.shape[0]
        if len(i[0]) == 0:
            self.tmp = np.array([[0.0, 1.0, 0.0, 0.0, 0.0] for _ in range(N)])
            return np.array([])
        if N == 1:
            self.tmp = np.array([[0.0, 1.0, 0.0, 0.0, 0.0]])
            return np.array([0 for _ in i[0]])
        Node_emb = self.models[0](X, sp_A)
        self.tmp = Node_emb.detach().numpy()
        Omega = torch.cat([Node_emb[i[0]],Node_emb[i[1]], X[i[0]], X[i[1]], Y],dim=1)
        E_pred = self.models[1](Omega).detach().numpy()
        rez = np.zeros_like(E_pred)
        rez[E_pred>0.5] = 1
        return rez
        
    def classifier(self, graph) -> int:
        pass

    def set_label_output_block(self, output_model, words, graph):
        # CLASSIFIER +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        for block in output_model.blocks:
            block_nodes = []
            for i, word in enumerate(words):
                if block.segment.is_intersection(word.segment):
                    block_nodes.append(self.tmp[i])
            block.tmp = np.array(block_nodes)
            class_ = int(np.argmax(np.array(block_nodes).mean(axis=0)))
            label = self.name_class[class_]
            block.set_label(label)