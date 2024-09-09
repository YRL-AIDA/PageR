import unittest
from pager import PageModel, PageModelUnit, WordsModel, SpGraph4NModel, WordsToSpGraph4N

class TestWords2SpGraph(unittest.TestCase):
    page = PageModel(page_units = [
                     PageModelUnit(id="word",
                                   sub_model=WordsModel(),
                                   extractors=[],
                                   converters={}),
                     PageModelUnit(id="graph",
                                   sub_model=SpGraph4NModel(), 
                                   extractors=[], 
                                   converters={"word": WordsToSpGraph4N()}),
])
    def test_graph(self) -> None:
        self.page.read_from_file('files/words8.json')
        self.page.extract()
        rez = self.page.to_dict()
        true_rez = {'A': [[0, 0, 0, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 7],
                          [0, 1, 2, 1, 7, 3, 3, 3, 4, 5, 5, 6, 7, 7]],
                    'nodes_feature': [17, 16, 12, 12, 14, 8, 8, 8],
                    'edges_feature': [0, 8, 24, 0, 21, 24, 25, 4, 33, 36, 5, 4, 5, 0]}
        for key in true_rez.keys():
            self.assertEqual(rez[key], true_rez[key])


