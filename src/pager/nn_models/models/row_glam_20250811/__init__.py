# from .model import get_final_model

from .torch_model import TorchModel
import torch
def get_load_model(path, device='cpu'):
    model = TorchModel({
        "sigmoidEdge": True,
        "node_featch": 15,
        "edge_featch": 4,
        "epochs": 80,
        "batch_size": 20,
        "learning_rate": 0.01,
        "Tag":[ {'in': -1, 'size': 128, 'out': 128, 'k': 3},
                {'in': 128, 'size': 64, 'out': 64, 'k': 3},
                {'in': 64, 'size': 32, 'out': 32, 'k': 3}],
        "NodeLinear": [-1, 64, 32],
        "NodeLinearClassifier": [16, 8],
        "EdgeLinear": [64],
        "NodeClasses": 5,
        "batchNormNode": True,
        "batchNormEdge": True,
        "seg_k": 0.5,
    })
    model.load_state_dict(torch.load(path, weights_only=True, map_location=torch.device(device)))
    return model