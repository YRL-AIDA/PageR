from ..base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from typing import Dict, List
from ..dtype import ImageSegment, Block, Word, Graph
from ..words_and_styles_model import WordsAndStylesModel 
from .graph_model import SpGraph4NModel, WordsAndStylesToSpGraph4N, WordsAndStylesToSpDelaunayGraph
import os
from .segmodel_utils import get_model as get_model_seg, classification_edges
from .classmodel_utils import get_model as get_model_class, classification_blocks

class PhisicalModel(BaseSubModel):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: List[Block] = []
    
    def from_dict(self, input_model_dict: Dict):
        pass

    def to_dict(self) -> Dict:
        return {"blocks": [block.to_dict() for block in self.blocks]}

    def read_from_file(self, path_file: str) -> None:
        phis_json = self._read_json(path_file)
        for block_dict in phis_json["blocks"]:
            self.blocks.append(Block(block_dict))

    def clean_model(self):
        self.blocks = []
    

class WordsToOneBlock(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        word_list: List[Word] = input_model.words
        segment = ImageSegment(0, 0, 1, 1)
        segment.set_segment_max_segments([word.segment for word in word_list])
        block = Block(segment.get_segment_2p())
        block.set_words_from_dict([word.to_dict() for word in word_list])
        output_model.blocks.append(block)

class WordsAndStylesToGNNBlocks(BaseConverter):
    def __init__(self, conf:Dict = {}) -> None:
        
        path_seg_model = conf['path_seg_model'] if "path_seg_model" in conf.keys() else os.environ["PATH_SEG_MODEL"] 
        path_class_model = conf['path_class_model'] if "path_class_model" in conf.keys() else  os.environ["PATH_CLASS_MODEL"]
        self.model_seg = get_model_seg(path_seg_model) 
        self.model_class = get_model_class(path_class_model) 
        self.name_class = ["no_struct", "text", "header", "list", "table"]
        self.spgraph = SpGraph4NModel()
        self.converter = conf['graph_converter'] if "graph_converter" in conf.keys() else  WordsAndStylesToSpGraph4N()
       
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        words = input_model.words        
        self.converter.convert(input_model, self.spgraph)
        graph = self.spgraph.to_dict()
        # SEGMENTER ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        edges_ind = classification_edges(self.model_seg, graph, k=0.5)
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
            # class_ = classification_blocks(self.model_class, sg)
            class_ = 1
            label = self.name_class[class_]
            block.set_label(label)
            
