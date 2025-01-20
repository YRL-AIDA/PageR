import numpy as np
import tensorflow as tf
from collections import defaultdict


def get_need_model(graph):
    if not graph["A"] or not graph["A"][0] or not graph["A"][1]:
        Mtrx = tf.eye(1, dtype=tf.float32)
        H0 = tf.ones([1, 9], dtype=tf.float32)
        # return tf.zeros([0, 0]), tf.zeros([0, 0])
        return Mtrx, H0
    else:
        N = max(max(graph["A"][0]) + 1, max(graph["A"][1]) + 1)

    indices_A = np.transpose(graph["A"])
    values = np.array([v if index[0] != index[1] else 1
                       for v, index in zip(graph["edges_feature"], indices_A)],
                      dtype=np.float32)

    index_dict = defaultdict(float)
    for idx, val in zip(indices_A, values):
        index_dict[tuple(idx)] += val

    indices_A = np.array(list(index_dict.keys()))
    values = np.array(list(index_dict.values()), dtype=np.float32)

    v = np.array(graph['nodes_feature'], dtype=np.float32)

    if len(v) != N:
        v = v[:N] if len(v) > N else np.pad(v, ((0, N - len(v)), (0, 0)), 'constant', constant_values=0)


    max_ = np.max(v, axis=0)
    min_ = np.min(v, axis=0)
    delta_ = max_ - min_

    for i in range(len(v[0])):
        v[:, i] = (max_[i] - v[:, i]) / delta_[i] if delta_[i] != 0 else v[:, i]

    H0 = tf.constant(v, dtype=tf.float32)

    A = tf.SparseTensor(indices=indices_A,
                        values=values,
                        dense_shape=[N, N])

    A = tf.sparse.reorder(A)
    A_with_I = tf.sparse.add(A, tf.sparse.eye(N))

    D_diag_values = tf.sparse.reduce_sum(A_with_I, axis=1)
    D_inv_sqrt_diag_values = tf.math.pow(D_diag_values, -0.5)
    D_inv_sqrt_indices = np.array([[i, i] for i in range(N)], dtype=np.int64)
    D_inv_sqrt = tf.SparseTensor(
        indices=D_inv_sqrt_indices,
        values=D_inv_sqrt_diag_values,
        dense_shape=[N, N]
    )

    temp = tf.sparse.sparse_dense_matmul(D_inv_sqrt, tf.sparse.to_dense(A_with_I))
    Mtrx = tf.sparse.sparse_dense_matmul(D_inv_sqrt, temp)

    return Mtrx, H0

def classification_blocks(model, graph):
    Mtrx, H0 = get_need_model(graph)
    label_pred = model(Mtrx, H0)
    a = np.argmax(label_pred)
    return a

params = {
    "count_neuron_layer_1": 9,
    "count_neuron_layer_2": 12,
    "output_size": 3,
}


def get_model(path=None):
    l1 = params["count_neuron_layer_1"]
    l2 = params["count_neuron_layer_2"]
    output_size = params["output_size"]
    model = BlockClassifier(l1, l2, output_size)
    # if path is None:
    #     return model
    load_model = tf.saved_model.load(path)
    model.conv1 = load_model.conv1
    model.conv2 = load_model.conv2
    model.output_layer = load_model.output_layer
    return load_model

class MyGraphConv(tf.Module):
    def __init__(self, input_size, output_size, activation_fun):
        self.W = tf.Variable(tf.random.normal(shape=[input_size, output_size], mean=0.1, stddev=1.0))
        self.B = tf.Variable(tf.random.normal(shape=[input_size, output_size], mean=1.0, stddev=1.0))
        self.activation = activation_fun

    def __call__(self, A, H):
        H_prime = self.activation(
            tf.matmul(tf.matmul(A, H), self.W) - tf.matmul(H, self.B)
        )
        return H_prime

class BlockClassifier(tf.Module):
    def __init__(self, l1, l2, output_size):
        self.conv1 = MyGraphConv(l1, l2, tf.nn.relu)
        self.conv2 = MyGraphConv(l2, output_size, tf.nn.relu)

        self.output_layer = tf.keras.layers.Dense(5, activation='softmax')

    @tf.function
    def __call__(self, A, H0):
        H1 = self.conv1(A, H0)
        H2 = self.conv2(A, H1)

        node_logits = self.output_layer(H2)

        output = tf.reduce_mean(node_logits, axis=0)

        return output

    def save(self, path):
        tf.saved_model.save(self, path)



