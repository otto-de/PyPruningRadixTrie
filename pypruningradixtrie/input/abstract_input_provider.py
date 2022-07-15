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
