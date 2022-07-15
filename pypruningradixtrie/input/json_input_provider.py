import json
import logging
from typing import List, Callable, Any, Dict

from pypruningradixtrie.input.abstract_input_provider import AbstractInputProvider
from pypruningradixtrie.input.input import Input


class JSONInputProvider(AbstractInputProvider):
    """
    InputProvider that uses JSON as source
    """

    def __init__(self, key_for_term: str, score_fun: Callable[[Dict[str, Any]], float]):
        """
        :param key_for_term: key in each entry that points to term to insert into PRT
        :param score_fun: function that takes json entry and returns a score as float

        :return InputProvider that reads a JSON file in the format of { "data" : [ {...}, {...}, {...} ] }
        """
        self.key_for_term: str = key_for_term
        self.score_fun: Callable[[Dict[str, Any]], float] = score_fun

    def read_input_data(self, file_path: str) -> List[Input]:
        """
        :param file_path: path to input file

        :return: List of Input objects
        """
        read_success_count: int = 0
        read_error_count: int = 0

        entries: List[Input] = []

        with open(file_path, 'r') as f:
            json_data = json.load(f)

            for entry in json_data["data"]:
                try:
                    entries.append(Input(entry[self.key_for_term], self.score_fun(entry)))
                    read_success_count += 1
                except Exception as _:
                    read_error_count += 1

        logging.info(f'Finished loading {read_success_count} entries from path {file_path}.'
                     f' Encountered {read_error_count} errors')

        # longest first, makes insert faster
        return sorted(entries, key=lambda x: len(x.query), reverse=True)
