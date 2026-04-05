class Font:
    def __init__(self, dict_font):
        self.name = ''
        self.width = 0.5
        self.italic = 0.0
        self.size = -1
        if type(dict_font) == dict:
            self.set_name(dict_font)
            self.set_width(dict_font)
            self.set_italic(dict_font)
            self.set_size(dict_font)


    def set_name(self, dict_font):
        if 'name' in dict_font:
            self.name = dict_font['name']
        elif 'fontname' in dict_font:
            self.name = dict_font['fontname']

    def set_width(self, dict_font):
        if 'width' in dict_font:
            self.width = dict_font['width']
        elif 'is_bold' in dict_font:
            self.width = 1.0 if dict_font['is_bold'] else 0.5  
        elif 'bold' in dict_font['fontname'].lower():
            self.width = 1.0
        else:
            self.width = 0.0
        

    def set_italic(self, dict_font):
        if 'italic' in dict_font:
            self.italic = dict_font['italic']
        elif 'is_italic' in dict_font:
            self.italic = 1.0 if dict_font['is_italic'] else 0.5  
        elif 'italic' in dict_font['fontname'].lower():
            self.italic = 1.0
        else:
            self.italic = 0.0

    def set_size(self, dict_font):
        if 'size' in dict_font:
            self.size = dict_font['size']
        elif 'fontsize' in dict_font:
            self.size = dict_font['fontsize']
        elif 'height' in dict_font:
            self.size = dict_font['height']
        else:
            self.size = -1

    def to_dict(self):
        return {
            'name': self.name,
            'width': self.width,
            'italic': self.italic,
            'size': self.size
        }
    
    def __lt__(self, other:'Font'):
        if self.size/other.size < 0.9:
            return True
        if self.width < 0.8 and other.width > 0.8:
            return True
        if self.width < 0.8 and other.width < 0.8 and \
          self.italic > 0.8 and other.italic < 0.8:
            return True
        return False
