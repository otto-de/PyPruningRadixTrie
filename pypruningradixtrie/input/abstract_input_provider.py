import abc
from typing import List

from pypruningradixtrie.input.input import Input


class AbstractInputProvider:
    """
    Parent class for different input providers
    """
    @staticmethod
    @abc.abstractmethod
    def read_input_data(file_path: str) -> List[Input]:
        raise NotImplementedError
    
    """
    Opens the input data stream. This is helpful when you want to use another library to read the file stream (e.g. smart_open, ...).
    """
    @staticmethod
    def open_file_stream(file_path: str):
        return open(file_path, 'r')
    
