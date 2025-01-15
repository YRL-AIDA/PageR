from ..base_sub_model import BaseSubModel, BaseExtractor, BaseConverter
from ..dtype import ImageSegment, Block, StyleWord
from typing import List
from sklearn.cluster import DBSCAN
import numpy as np


class WordsToDBSCANBlocks(BaseConverter):
    def convert(self, input_model: BaseSubModel, output_model: BaseSubModel)-> None:
        word_list: List[StyleWord] = input_model.words

        blocks = self.get_blocks_from_words(word_list)
        for block in blocks:
            output_model.blocks.append(block)
       
    def get_blocks_from_words(self, word_list: List[StyleWord]) -> List[Block]:
        word_chars_index = []
        char_coordinate = []
        list_h = []
        for j, word in enumerate(word_list):
            seg = word.segment.get_segment_2p()
            w = word.segment.get_width()
            h = word.segment.get_height()
            list_h.append(h)
            n = len(word.content)
            dx = w/n
            x0 =seg["x_top_left"] + dx/2
            y = seg["y_top_left"] + h/2
            for i in range(n):
                word_chars_index.append(j)
                char_coordinate.append((x0 + i*dx, y))
        mean_h = np.mean(list_h)
        clusters = DBSCAN(eps=3*mean_h).fit(char_coordinate)
        m = max(clusters.labels_)
        blocks = []
        for i in range(-1, m+1):
            word_clust_list = []
            for j, char_label in enumerate(clusters.labels_):
                if char_label == i:
                    tmp_word = word_list[word_chars_index[j]]
                    if not tmp_word in word_clust_list:
                        word_clust_list.append(tmp_word)
            if len(word_clust_list) != 0:    
                segment = ImageSegment(0, 0, 1, 1)
                segment.set_segment_max_segments([word.segment for word in word_clust_list])
                block = Block(segment.get_segment_2p())
                # TODO: Решить проблему с типами в блоке (+1)
                words_ = [word.to_dict()['segment'] for word in word_clust_list]
                for word_, word in zip(words_, word_clust_list):
                    word_["text"] = word.content
                block.set_words_from_dict(words_)
                block.set_label("text")
                blocks.append(block)
            
        return blocks
        