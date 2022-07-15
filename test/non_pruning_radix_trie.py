from typing import List

from pypruningradixtrie.entry import Entry
from pypruningradixtrie.trie import PruningRadixTrie
from pypruningradixtrie.trie_node import TrieNode


class NonPruningRadixTrie(PruningRadixTrie):
    def _should_skip_node_and_all_children(self, node: TrieNode, results: List[Entry], top_k: int) -> bool:
        """
        :param node: root of possible new branch to look through
        :param results: results that were already collected
        :param top_k: number of results that we want to collect

        :return: always False to make behaviour non-pruning
        """

        return False

    @staticmethod
    def _should_skip_all_children_of_node(node: TrieNode,
                                          results: List[Entry],
                                          top_k: int) -> bool:
        """
        :param node: root of possible new branch to look through
        :param results: results that were already collected
        :param top_k: number of results that we want to collect

        :return: always False to make behaviour non-pruning
        """

        return False
