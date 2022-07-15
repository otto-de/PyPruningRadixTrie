import dataclasses
from typing import List, Tuple


@dataclasses.dataclass
class TrieNode:
    def __init__(self, score):
        self.__score: float = score
        self.is_word_end: bool = score > 0

        self.children: List[Tuple[str, TrieNode]] = []
        self.max_score_children: float = 0

    def add_child(self, term: str, node):
        if not self.children:
            self.children = [(term, node)]
        else:
            self.children.append((term, node))

        self.__sort_children()

    def has_children(self) -> bool:
        return len(self.children) > 0

    def get_score(self) -> float:
        return self.__score

    def set_score(self, score) -> None:
        self.__score = score
        self.is_word_end = self.__score > 0

    def add_to_score(self, score) -> None:
        self.__score += score
        self.is_word_end = self.__score > 0

    def replace_child(self, term: str, node, index: int):
        self.children[index] = (term, node)

        self.__sort_children()

    def __sort_children(self):
        self.children = sorted(self.children, key=lambda x: x[1].max_score_children, reverse=True)
