import torch
from torch_geometric.nn import BatchNorm, TAGConv
from torch.nn import Linear
from torch.nn.functional import relu

def get_tensor_from_graph(graph):    
    i = graph["A"]
    v_in = [1 for e in graph["edges_feature"]]
    y = graph["edges_feature"]
    x = graph["nodes_feature"]
    N = len(x)
    
    X = torch.tensor(data=x, dtype=torch.float32)
    Y = torch.tensor(data=y, dtype=torch.float32)
    sp_A = torch.sparse_coo_tensor(indices=i, values=v_in, size=(N, N), dtype=torch.float32)
    return X, Y, sp_A, i

def load_weigths(models, path_node_gnn, path_edge_linear):
    models[0].load_state_dict(torch.load(path_node_gnn, weights_only=True))
    models[1].load_state_dict(torch.load(path_edge_linear, weights_only=True))
    return models

class NodeGLAM(torch.nn.Module):
    def __init__(self,  input_, h, output_):
        super(NodeGLAM, self).__init__()
        self.batch_norm1 = BatchNorm(input_)
        self.linear1 = Linear(input_, h[0]) 
        self.tag1 = TAGConv(h[0], h[1])
        self.linear2 = Linear(h[1], h[2]) 
        self.tag2 = TAGConv(h[2], h[3])
        self.linear3 = Linear(h[3]+input_, h[4])
        self.linear4 =Linear(h[4], output_)

    
    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        x = self.batch_norm1(x)
        h = self.linear1(x)
        h = relu(h)
        h = self.tag1(h, edge_index)
        h = relu(h)
        
        h = self.linear2(h)
        h = relu(h)
        h = self.tag2(h, edge_index)
        h = relu(h)
        a = torch.cat([x, h], dim=1)
        a = self.linear3(a)
        a = relu(a)
        a = self.linear4(a)
        return torch.softmax(a, dim=-1)

class EdgeGLAM(torch.nn.Module):
    def __init__(self, input_, h, output_):
        super(EdgeGLAM, self).__init__()
        self.batch_norm2 = BatchNorm(input_, output_)
        self.linear1 = Linear(input_, h[0]) 
        self.linear2 = Linear(h[0], output_)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.batch_norm2(x)
        h = self.linear1(x)
        h = relu(h)
        h = self.linear2(h)
        h = torch.sigmoid(h)
        return torch.squeeze(h, 1)