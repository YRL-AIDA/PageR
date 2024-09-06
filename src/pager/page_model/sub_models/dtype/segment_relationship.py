from typing import List, Dict, Tuple, Set


class Node:
    def __init__(self, x: float, y: float, index: int):
        self.x = x
        self.y = y
        self.index = index
        self.neighbors = []

    def __str__(self):
        return f"({self.x:.2f}, {self.y:.2f})"

    def add_neighbor(self, node: "Node"):
        self.neighbors.append(node)

    def get_neighbors(self) -> Set["Node"]:
        return set(self.neighbors)


class Edge:
    def __init__(self, nodes: Set[Node]):
        self.nodes = nodes

    def get_line(self) -> Tuple[List[float], List[float]]:
        x = []
        y = []
        for node in self.nodes:
            x.append(node.x)
            y.append(node.y)

        return x, y

    def get_nodes(self) -> List[Node]:
        return list(self.nodes)


class NoneNode(Node):
    def __init__(self):
        super(NoneNode, self).__init__(0, 0, 0)
        self.x = None
        self.y = None
        self.index = None


class RelatedGraph:
    def __init__(self, node: Node):
        self.nodes = {node: node.index}
        self.edges = dict()

    def get_nodes(self) -> List[Node]:
        return list(self.nodes.keys())

    def add_node(self, node: Node, node_connect: Node):
        if not (node_connect in self.nodes):
            print("НЕТ УЗЛА ДЛЯ СОЕДИНЕНИЯ")
            return
        if not (node in self.nodes):
            self.nodes[node] = node.index
        self.add_edge(node, node_connect)

    def add_edge(self, node1: Node, node2: Node):
        if not (node1 in self.nodes) or not (node2 in self.nodes):
            print("НЕТ ТАКИХ УЗЛОВ")
            return
        keys_edge = tuple({self.nodes[node1], self.nodes[node2]})
        if keys_edge in self.edges:
            print("УЗЕЛ УЖЕ ЕСТЬ")
        self.edges[keys_edge] = Edge({node1, node2})
        node1.add_neighbor(node2)
        node2.add_neighbor(node1)

    def get_edges(self) -> List[Edge]:
        return [edge for key_edge, edge in self.edges.items()]

    def get_edge_from_nodes(self, node1: Node, node2: Node) -> Edge:
        key_edge = tuple({self.nodes[node1], self.nodes[node2]})
        return self.edges[key_edge]

    def delete_edge(self, edge: Edge):
        node1, node2 = edge.get_nodes()
        self.delete_edge_from_nodes(node1, node2)

    def delete_edge_from_nodes(self, node1: Node, node2: Node) -> List["RelatedGraph"]:
        key_edge = tuple({self.nodes[node1], self.nodes[node2]})
        self.edges.pop(key_edge)

        node1.neighbors.remove(node2)
        node2.neighbors.remove(node1)

        neighbors_node1 = node1.get_neighbors()
        neighbors_node2 = node2.get_neighbors()

        graph1_nodes = []
        graph1_edges_key = set()
        sub_set = neighbors_node1.intersection(neighbors_node2)
        if len(sub_set) > 0:
            return [self]

        nodes = neighbors_node1 - sub_set

        while len(nodes) != 0:
            node = nodes.pop()
            if not (node in graph1_nodes):
                graph1_nodes.append(node)
            if node == node2:
                return [self]
            nodes_new = node.get_neighbors()
            for node_new in nodes_new:
                keys_edge_new = tuple({self.nodes[node_new], self.nodes[node]})
                graph1_edges_key.add(keys_edge_new)
            nodes.union(nodes_new)

        graph2_edges_key = set(self.edges.keys()) - graph1_edges_key
        graph1 = self.create_related_graph(graph1_edges_key)
        graph2 = self.create_related_graph(graph2_edges_key)
        return [graph1, graph2]

    def create_related_graph(self, edges_key) -> "RelatedGraph":
        none_node = NoneNode()
        r = RelatedGraph(none_node)

        for key in edges_key:
            r.edges[key] = self.edges[key]

        nodes = set()
        for key in edges_key:
            n1, n2 = self.edges[key].get_nodes()
            nodes.add(n1)
            nodes.add(n2)

        for node in nodes:
            r.nodes[node] = node.index

        r.nodes.pop(none_node)
        return r

    def add_related_graph(self, other_related_graph: "RelatedGraph", this_node: Node, other_node):
        for node in other_related_graph.get_nodes():
            self.nodes[node] = node.index

        for key, edge in other_related_graph.edges.items():
            self.edges[key] = edge

        self.add_edge(other_node, this_node)


class Graph:
    def __init__(self):
        self.related_graphs: Set[RelatedGraph] = set()
        self.nodes: Dict[int, Node] = dict()
        self.nodes_in_graphs: Dict[int, RelatedGraph] = dict()
        self.id_cursor = 0

    def get_edges(self) -> List[Edge]:
        return [edge for r in self.related_graphs for edge in r.get_edges()]

    def get_nodes(self) -> List[Node]:
        return [node for r in self.related_graphs for node in r.get_nodes()]

    def get_node(self, index) -> Node:
        return self.nodes[index]

    def get_related_graphs(self) -> List[RelatedGraph]:
        return list(self.related_graphs)

    def get_related_graph_from_index_node(self, index_node: int) -> RelatedGraph:
        return self.nodes_in_graphs[index_node]

    def add_node(self, x: float, y: float) -> int:
        self.id_cursor += 1
        node = Node(x, y, self.id_cursor)
        self.nodes[self.id_cursor] = node

        r = RelatedGraph(node)
        self.nodes_in_graphs[self.id_cursor] = r
        self.related_graphs.add(r)

        return self.id_cursor

    def add_edge(self, index_node1: int, index_node2):
        n1, r1 = self._get_couple_node_related_graph(index_node1)
        n2, r2 = self._get_couple_node_related_graph(index_node2)

        if r1 == r2:
            r1.add_edge(n1, n2)
        else:
            self.related_graphs.remove(r2)
            r1.add_related_graph(this_node=n1, other_related_graph=r2, other_node=n2)
            keys = [key for key, node in self.nodes.items() if node in r1.get_nodes()]
            for key in keys:
                self.nodes_in_graphs[key] = r1

    def delete_edge(self, index_node1, index_node2):
        n1 = self.get_node(index_node1)
        n2 = self.get_node(index_node2)
        r = self.get_related_graph_from_index_node(index_node1)
        new_r = r.delete_edge_from_nodes(n1, n2)
        if len(new_r) == 2:
            self.related_graphs.remove(r)
            self.related_graphs.add(new_r[0])
            self.related_graphs.add(new_r[1])
            for index in [0, 1]:
                keys = [key for key, node in self.nodes.items() if node in new_r[index].get_nodes()]
                for key in keys:
                    self.nodes_in_graphs[key] = new_r[index]

    def _get_couple_node_related_graph(self, index) -> Tuple[Node, RelatedGraph]:
        return self.get_node(index), self.nodes_in_graphs[index]
