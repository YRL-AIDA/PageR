from abc import ABC, abstractmethod
from datetime import date


class BaseBenchmark(ABC):
    def __init__(self):
        self.name = f"{str(date.today())}" 
        self.loger = LogerBenchmark(f'{self.name}.txt')
        self.loger("S T A R T")
        self.start()
        
    def __str__(self):
        return self.name
        
    @abstractmethod   
    def start(self):
        pass
        
    
        
class LogerBenchmark:
    def __init__(self, path_file):
        self.path = path_file

    def __call__(self, text_log):
        with open(self.path, 'a') as f:
            f.write(text_log + '\n')

