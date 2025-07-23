class ConteinImage(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return f"Model 'WordsModel' not have image"
    

class ConteinNumPage(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return f"Model 'PrecisionPDFModel' not have num_page"