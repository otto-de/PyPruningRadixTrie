import csv
import logging
from typing import List, Callable

from pypruningradixtrie.input.abstract_input_provider import AbstractInputProvider
from pypruningradixtrie.input.input import Input


class CSVInputProvider(AbstractInputProvider):
    """
    InputProvider that uses CSV as source
    """

    def __init__(self, seperator: str, score_fun: Callable[[List[str]], float], term_index: int = 0):
        """
        :param seperator: separator for CSV entries
        :param score_fun: function to calculate the score from CSV line entries
        :param term_index: index in CSV line where term to insert into trie is located

        :return InputProvider that reads CSV
        """
        self.seperator: str = seperator
        self.term_index: int = term_index
        self.score_fun: Callable[[List[str]], float] = score_fun

    def read_input_data(self, file_path: str) -> List[Input]:
        """
        :param file_path: path to input file

        :return: List of Input objects
        """
        read_success_count: int = 0
        read_error_count: int = 0

        entries: List[Input] = []

        with open(file_path, 'r') as f:
            reader = csv.reader(f, delimiter=self.seperator)
            # skip header
            next(reader)

            for line in reader:
                try:
                    entries.append(Input(line[self.term_index], self.score_fun(line)))
                    read_success_count += 1
                except Exception as _:
                    read_error_count += 1

        logging.info(f'Finished loading {read_success_count} entries from path {file_path}.'
                     f' Encountered {read_error_count} errors')

        # longest first, makes insert faster
        return sorted(entries, key=lambda x: len(x.query), reverse=True)
