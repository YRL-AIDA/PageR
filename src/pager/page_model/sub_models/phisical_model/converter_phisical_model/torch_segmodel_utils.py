import torch
from torch_geometric.nn import GCNConv
from torch.nn import Linear
from torch.nn.functional import relu, sigmoid
import numpy as np

class GNN(torch.nn.Module):
    def __init__(self,  layers):
        super(GNN, self).__init__()
        convs = []
        Bs = []
        for l_in, l_out in zip(layers[:-1], layers[1:]):
            convs.append(GCNConv(l_in, l_out, bias=False))
            torch.nn.init.normal_(convs[-1].lin.weight,mean=0.01, std=0.3)
            Bs.append(torch.nn.Linear(l_in, l_out, bias=False))
            torch.nn.init.normal_(Bs[-1].weight, mean=0.5, std=0.3)
        self.convs = torch.nn.ModuleList(convs)
        self.Bs = torch.nn.ModuleList(Bs)

    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        for conv, B in zip(self.convs, self.Bs):
            x = conv(x, edge_index) -  B(x)
            x = relu(x)
        return x

class EdgesMLP(torch.nn.Module):
    def __init__(self, layers):
        super(EdgesMLP, self).__init__()
        linears = []
        for l_in, l_out in zip(layers[:-1], layers[1:]):
            linears.append(Linear(l_in, l_out, bias=False))
            torch.nn.init.normal_(linears[-1].weight, mean=0.5, std=0.3)
        self.linears = linears

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for linear in self.linears:
            x = linear(x)
            x = sigmoid(x)
        return torch.squeeze(x, 1)

def get_models(params):
    layers_gnn = params["count_neuron_layers_gnn"]
    layers_edge = params["count_neuron_layers_edge"]
    node_gnn = GNN(layers_gnn)
    edge_linear = EdgesMLP(layers_edge)
    return node_gnn, edge_linear

def rev_dist(a):
    if a==0:
        return 0
    else:
        return 1/a

def get_tensor_from_graph(graph):
    i = graph["A"]
    v_in = [rev_dist(e) for e in graph["edges_feature"]]
    v_true = graph["true_edges"]
    x = graph["nodes_feature"]
    N = len(x)
    
    X = torch.tensor(data=x, dtype=torch.float32)
    sp_A = torch.sparse_coo_tensor(indices=i, values=v_in, size=(N, N), dtype=torch.float32)
    E_true = torch.tensor(data=v_true, dtype=torch.float32)
    return X, sp_A, E_true, i


def load_weigths(models, path_node_gnn, path_edge_linear):
    models[0].load_state_dict(torch.load(path_node_gnn, weights_only=True))
    models[1].load_state_dict(torch.load(path_edge_linear, weights_only=True))
    return models

def get_segmenter(params):
    models_load = get_models(params)
    rez_models = load_weigths(models_load, params["path_node_gnn"], params["path_edge_linear"])
    return rez_models

def torch_classification_edges(models, graph, k=0.51):
    i = graph["A"]
    v_in = [rev_dist(e) for e in graph["edges_feature"]]
    x = graph["nodes_feature"]
    N = len(x)
    X = torch.tensor(data=x, dtype=torch.float32)
    sp_A = torch.sparse_coo_tensor(indices=i, values=v_in, size=(N, N), dtype=torch.float32)
    
    H_end = models[0](X, sp_A)
    Omega = torch.cat([H_end[i[0]], H_end[i[1]]],dim=1)
    E_pred = models[1](Omega)
    a = np.zeros(E_pred.shape)
    a[E_pred>k] = 1.0
    return a
   