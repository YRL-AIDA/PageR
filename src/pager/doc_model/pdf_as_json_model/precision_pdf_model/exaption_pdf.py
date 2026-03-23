class NotThisNumberPage(Exception):
    def __init__(self, num):
        self.num = num
    def __str__(self) -> str:
        return f'Not this {self.num} page'

class NotMethodParsing(Exception):
    def __init__(self):
        pass

    def __str__(self) -> str:
        return '''No method ('r', 'w') is specified
    PDFModel(conf={'method': 'name_method'})
or
    .read_from_file(..., method='name_method')
    '''

class MethodConflict(Exception):
    def __init__(self, method1, method2):
        self.m1 = method1
        self.m2 = method2
        pass

    def __str__(self) -> str:
        return f'''self.method = '{self.m1}' and method = '{self.m2}' is conflict 
    '''