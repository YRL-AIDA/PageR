from ..base_sub_model import BaseConverter
from ..pdf_model import PDFModel
from ..words_model import WordsModel
from ..dtype import Word

class PDF2Words(BaseConverter):
    def convert(self, input_model: PDFModel, output_model: WordsModel):
        page_json = input_model.to_dict()
        word_list = self.get_words(page_json['words'])
        output_model.words = word_list

    def get_words(self, words_json):
        words = []
        for word in words_json:
            if word["height"] < 1 or word["width"] < 1:
                continue
            # tmp_style = self.get_style_from_word(word)
            # index_style = self._get_style(tmp_style, styles)           
            # if index_style == -1:
            #     tmp_style.id = index_style
            #     styles.append(tmp_style)
            #     index_style = len(styles) - 1 
            # words.append(Word({"style_id": index_style,
            #             "content": word["text"],
            #             "segment": word,
            #             "type_align": None}))
            word["segment"] = word 
            words.append(Word(word))
        return words


    # def _get_style(self, style, styles):
    #     for i, style_ in enumerate(styles):
    #         if style_ == style: # TODO: экземпляры разные, проверять надо по значениям
    #             return i
    #     return -1

    # def get_style_from_word(self, word) -> Style:
    #     return Style({    
    #             "id": None,
    #             "size": word["font_size"],
    #             "font_type": word["font_type"],
    #             "italic": word["italic"],
    #             "width": 1.0 if word["bold"] else 0.0
    #         })