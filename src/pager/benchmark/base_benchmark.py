from abc import ABC, abstractmethod
from datetime import date
from typing import Dict

class DocumentsBenchmark(ABC):
    def __init__(self, count):
        self.i = -1
        self.n = count

    @abstractmethod
    def get_i_true(self):
        pass

    @abstractmethod
    def get_i_pred(self):
        pass

    def __next__(self):
        if self.i == self.n-1:
            print("stop")
            raise StopIteration
        else:  
            self.i += 1
            return self.get_i_true(), self.get_i_pred()
        

    def __iter__(self):
        return self
        

class BaseBenchmark(ABC):
    def __init__(self):
        self.documents = self.get_documents()
        self.name = f"{str(date.today())}" 
        self.loger = LogerBenchmark(f'{self.name}.txt')
        self.loger("S T A R T")
        self.__start()
        
    def __str__(self):
        return self.name
    
    @abstractmethod    
    def get_documents(self) -> DocumentsBenchmark:
        pass

    @abstractmethod    
    def test_one_document(self, document) -> Dict[str, float]:
        pass

    def test_more_documents(self, documents):  
        rez = []  
        for document in documents:
            rez.append(self.test_one_document(document))
            
        
        n = len(rez)
        for key in rez[0].keys():
            metric = [rez_i[key] for rez_i in rez if rez_i[key] != None] 
            val = sum(metric)/len(metric) if len(metric) != 0 else "None"
            self.loger(f"{key} = {val}")
        
        
    def __start(self):
        self.test_more_documents(self.documents)
        
    
        
class LogerBenchmark:
    def __init__(self, path_file):
        self.path = path_file

    def __call__(self, text_log):
        with open(self.path, 'a') as f:
            f.write(text_log + '\n')

