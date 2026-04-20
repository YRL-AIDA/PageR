from .page import Page
from typing import List

class Document:
    def __init__(self, pages: List[Page]):
        self.pages = pages


    @property
    def md(self):
        text = ''
        for page in self.pages:
            text += page.md
            text += f'\n<!-- page_num: {page.num_page} --> \n'
            text += '---'
        return  text    