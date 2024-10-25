import numpy as np
import tensorflow as tf

params = {
    "start_w": 0.01,
    "start_b": 0.1,
    "count_neuron_layer_1": 9,
    "count_neuron_layer_2": 18,
    "count_neuron_layer_end": 9,
}


def get_need_model(graph):
    N = len(graph['nodes_feature'])#max(max(graph["A"][0])+1, max(graph["A"][1])+1)
    indices_A = np.transpose(graph["A"])
    
    v = np.array(graph['nodes_feature'], dtype=np.float32)
    max_ = np.max(v, axis=0)
    min_ = np.min(v, axis=0)
    delta_ = max_- min_
    
    # for i in range(len(v[0])):
    for i in range(2):
        v[:, i] = (max_[i] - v[:, i])/delta_[i] if delta_[i] != 0 else v[:, i]
    H0 = tf.constant(v[:, :])
    A = tf.SparseTensor(indices=indices_A,
                    values=np.array([v + 0 if index[0] != index[1] else 1
                                     for v, index in zip(graph["edges_feature"], np.transpose(graph["A"]))], dtype=np.float32), 
                    dense_shape=[N, N])
    d = tf.sparse.reduce_sum(A, axis=1)
    Mtrx = tf.SparseTensor(indices=indices_A,
                    values=np.array([val/d[index[0]] for index, val in zip(A.indices, A.values)], dtype=np.float32), 
                    dense_shape=[N, N])
    
    s1 = tf.SparseTensor(indices=[[i, e0] for i, e0 in enumerate(graph["A"][0])],
                    values=np.ones_like(graph["A"][0], dtype=np.float32), 
                    dense_shape=[len(graph["A"][0]), N])
    s2 = tf.SparseTensor(indices=[[i, e1] for i, e1 in enumerate(graph["A"][1])],
                    values=np.ones_like(graph["A"][1], dtype=np.float32), 
                    dense_shape=[len(graph["A"][1]), N])
    return Mtrx, H0, s1, s2
    
def classification_edges(model, graph, k=0.51):
    Mtrx, H0, s1, s2 = get_need_model(graph)
    h1 =  model(Mtrx, H0, s1, s2)
    a = np.zeros_like(h1)
    a[h1>k] = 1.0
    return a


def get_model(path=None):
    l1 = params["count_neuron_layer_1"]
    l2 = params["count_neuron_layer_2"]
    l3 = params["count_neuron_layer_end"]
    model = GraphSegmenter(l1, l2, l3)
    if path is None:
        return model
    load_model = tf.saved_model.load(path)
   
    model.conv1.W = load_model.conv1.W
    model.conv1.B = load_model.conv1.B
    model.conv2.W = load_model.conv2.W
    model.conv2.B = load_model.conv2.B
    return model


class MyEndLayer(tf.Module):
    def __call__(self, s1, s2, h): 
        left_ = tf.sparse.sparse_dense_matmul(s1, h)
        right_ = tf.sparse.sparse_dense_matmul(s2, h)
        # return tf.reduce_sum(left_norm * right_norm, axis=1)
        return 0.5*(1.0-tf.losses.cosine_similarity(left_ , right_)) 
        
        

class MyGraphConv(tf.Module):
    def __init__(self, input_size, outpu_size, activation_fun):
        self.W = tf.Variable(tf.random.normal(mean=params["start_w"], stddev=1.0, shape=[input_size, outpu_size]))
        self.B = tf.Variable(tf.random.normal(mean=params["start_b"], stddev=1.0, shape=[input_size, outpu_size]))
        self.activation = activation_fun

    def __call__(self, A, H0):
        H1 = self.activation(
            tf.matmul(tf.sparse.sparse_dense_matmul(A, H0), self.W) - tf.matmul(H0, self.B)
        )
        return H1

class GraphSegmenter(tf.Module):
    def __init__(self, l1, l2, l3):
        self.conv1 = MyGraphConv(l1, l2, tf.nn.relu)
        self.conv2 = MyGraphConv(l2, l3, tf.nn.relu)
        self.end_layer = MyEndLayer()

    @tf.function
    def __call__(self, A, H0, s1, s2):
        H1 = self.conv1(A, H0)
        H2 = self.conv2(A, H1)
        return self.end_layer(s1, s2, H2)

    def save(self, path):
        tf.saved_model.save(self, path)


