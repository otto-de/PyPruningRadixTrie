import os
import unittest

from pypruningradixtrie.entry import Entry
from pypruningradixtrie.input.csv_input_provider import CSVInputProvider
from pypruningradixtrie.trie import PruningRadixTrie
from pypruningradixtrie.trie_node import TrieNode

base_path = os.path.join(os.path.dirname(__file__), '_resources')


class TestPruningRadixTrieQuery(unittest.TestCase):
    def base_trie(self):
        return PruningRadixTrie(f'{base_path}/test_data.csv', CSVInputProvider(',', lambda x: float(x[1]), 0))

    def test_query_returns_only_top_k(self):
        trie: PruningRadixTrie = self.base_trie()

        results = trie.get_top_k_for_prefix("f", 5)

        assert results == [Entry(term='flower power', score=1337),
                           Entry(term='flawless', score=98),
                           Entry(term='funky', score=96),
                           Entry(term='fancy', score=84),
                           Entry(term='flaw', score=79)]

    def test_query_returns_all_terms(self):
        trie: PruningRadixTrie = self.base_trie()

        results = trie.get_top_k_for_prefix("f", 200)

        assert results == [Entry(term='flower power', score=1337),
                           Entry(term='flawless', score=98),
                           Entry(term='funky', score=96),
                           Entry(term='fancy', score=84),
                           Entry(term='flaw', score=79),
                           Entry(term='flower', score=45),
                           Entry(term='flowchart', score=17),
                           Entry(term='flaky', score=12)]

    def test_query_with_long_prefix(self):
        trie: PruningRadixTrie = self.base_trie()

        results = trie.get_top_k_for_prefix("flower", 2)

        assert results == [Entry(term='flower power', score=1337), Entry(term='flower', score=45)]

    def test_query_not_existing(self):
        trie: PruningRadixTrie = self.base_trie()

        results = trie.get_top_k_for_prefix("not in the trie", 2)

        assert results == []

    def test_query_zero_or_negative_does_not_break(self):
        trie: PruningRadixTrie = self.base_trie()

        results = trie.get_top_k_for_prefix("foo", 0)

        assert results == []

        results = trie.get_top_k_for_prefix("foo", -1)

        assert results == []

    def test_should_skip_node_and_children_only_if_enough_results(self):
        trie = PruningRadixTrie()

        results = [Entry(term='flower power', score=1337),
                   Entry(term='flawless', score=98),
                   Entry(term='funky', score=96)]

        node = TrieNode(42)
        node.max_score_children = 23

        would_skip: bool = trie._should_skip_node_and_all_children(node, results, top_k=3)

        assert would_skip is True

        would_skip: bool = trie._should_skip_node_and_all_children(node, results, top_k=4)

        assert would_skip is False

    def test_should_not_skip_node_and_children_if_score_high(self):
        trie = PruningRadixTrie()

        results = [Entry(term='flower power', score=1337),
                   Entry(term='flawless', score=98),
                   Entry(term='funky', score=96)]

        # parent score high
        node = TrieNode(123)
        node.max_score_children = 23

        would_skip: bool = trie._should_skip_node_and_all_children(node, results, top_k=2)

        assert would_skip is False

        # child score high
        node = TrieNode(2)
        node.max_score_children = 999

        would_skip: bool = trie._should_skip_node_and_all_children(node, results, top_k=2)

        assert would_skip is False
