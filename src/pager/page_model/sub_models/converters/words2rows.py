from ..base_sub_model import BaseConverter
from ..words_model import WordsModel
from ..rows_model import RowsModel
from ..dtype import ImageSegment, Row
from pager.nn_models.manager_models import ManagerModels
from ..dtype import Graph



class Words2Rows(BaseConverter):
    def __init__(self, conf={}):
        manager_model = ManagerModels()
        self.words2rowsGLAM_tokenizer = manager_model.get_model("wordGLAM-tokenizer")
        self.words2rowsGLAM = manager_model.get_model("words2rowsGLAM-model")

    def convert(self, input_model: WordsModel, output_model: RowsModel):
        page_json = input_model.to_dict()
        row_list = self.get_row(page_json['words'])
        output_model.from_dict({"rows": row_list})

        # сортировка после создания региона
        # sorter = RegionSorterCutXYExtractor()
        # sorter.extract(output_model)

    def get_row(self, words_json):
        graph_dict_torch = self.words2rowsGLAM_tokenizer(words_json)
        if graph_dict_torch['N'] < 2 or len(graph_dict_torch['inds'][0]) < 2:
            return [{'words': words_json}]

        result = self.words2rowsGLAM(graph_dict_torch)
        result['deleted_edges'] = result['E_pred'] > 0.5
        
        graph = graph_dict_torch['inds']
        deleted_edges = result['deleted_edges']
        
        regions = self.rows_from_graph(words_json, graph, deleted_edges)
        return regions
    

    def rows_from_graph(self, words_json, graph, deleted_edges):
        graph_ = Graph()
        rows = []
        
        for word_json in words_json:
            segment = ImageSegment(dict_2p=word_json['segment'])
            xc, yc = segment.get_center()
            graph_.add_node(xc, yc)

        for node_i, node_j, ind in zip(graph[0], graph[1], deleted_edges):
            if not ind:
                graph_.add_edge(node_i+1, node_j+1)

        for reg in graph_.get_related_graphs():
            indexes = [node.index-1 for node in reg.get_nodes()]
            rows.append({'words': [words_json[i] for i in indexes]})
        return rows
    


def obj_words2rows(words):
    words_dict = [w.to_dict() for w in words] 
    rows_dict = dict_words2rows(words_dict)
    return [Row(row_dict) for row_dict in rows_dict]
    

def dict_words2rows(dict_words):
    converter = Words2Rows()
    model_rows = RowsModel()
    model_words = WordsModel()

    model_words.set_words_from_dict(dict_words)
    converter.convert(model_words, model_rows)
    rows = model_rows.to_dict()['rows']
    return rows