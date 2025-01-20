from .segmodel_utils import get_model as get_model_seg, classification_edges 
from .classmodel_utils import get_model as get_model_class, classification_blocks
from ..converter_graph_model import SpGraph4NModel, WordsAndStylesToSpGraph4N
from ...base_sub_model import BaseSubModel, BaseConverter
from typing import Dict, List
from ...dtype import ImageSegment, Block, Graph
import os

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
            class_ = 1
            label = self.name_class[class_]
            block.set_label(label)

    def segmenter(self, graph) -> List[int]:
        pass

    def classifier(self, graph) -> int:
        pass
        

class WordsAndStylesToGNNBlocks(EdgeSegNodeClassConverter):
    def __init__(self, conf:Dict = {}) -> None:
        super().__init__(conf)
        path_seg_model = conf['path_seg_model'] if "path_seg_model" in conf.keys() else os.environ["PATH_SEG_MODEL"] 
        path_class_model = conf['path_class_model'] if "path_class_model" in conf.keys() else  os.environ["PATH_CLASS_MODEL"]
        self.model_seg = get_model_seg(path_seg_model) 
        self.model_class = get_model_class(path_class_model) 
        self.seg_k = conf['seg_k'] if "seg_k" in conf.keys() else 0.5

    def segmenter(self, graph) -> List[int]:
        return classification_edges(self.model_seg, graph, self.seg_k)
    
    def classifier(self, graph) -> int:
        # return classification_blocks(self.model_class, graph)
        return 1
        