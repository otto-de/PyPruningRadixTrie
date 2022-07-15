import os
import unittest
from typing import Any, Dict

from pypruningradixtrie.input.csv_input_provider import CSVInputProvider
from pypruningradixtrie.input.json_input_provider import JSONInputProvider
from pypruningradixtrie.insert import insert_term
from pypruningradixtrie.trie import PruningRadixTrie
from pypruningradixtrie.trie_node import TrieNode

base_path = os.path.join(os.path.dirname(__file__), '_resources')


class TestPruningRadixTrieInsert(unittest.TestCase):
    def test_insert_data_from_csv_file(self):
        trie = PruningRadixTrie(f'{base_path}/test_data.csv', CSVInputProvider(',', lambda x: float(x[1]), 0))

        assert trie.get_num_entries() == 12 - 4  # there are 4 duplicated entries in the example data

    def test_insert_data_from_complex_csv_file(self):
        trie = PruningRadixTrie(f'{base_path}/test_data_complex.csv',
                                CSVInputProvider(',', lambda x: float(x[0]) + float(x[2]), 1))

        assert trie.get_num_entries() == 3
        node, _ = trie._get_node_by_term("flower power")

        assert node.is_word_end is True
        assert node.get_score() == float(1337 + 8)

    def test_insert_data_from_json_file(self):
        def score_fun(json_entry: Dict[str, Any]) -> float:
            return json_entry["pages"] * (json_entry["year"] / 10.0)

        trie = PruningRadixTrie(f'{base_path}/test_data.json', JSONInputProvider("title", score_fun))

        assert trie.get_num_entries() == 5
        node, _ = trie._get_node_by_term("book about flowers")

        assert node.is_word_end is True
        assert node.get_score() == 1563 * 2021 / 10.0

    def test_insert_duplicate_entry_sums_up_score(self):
        trie = PruningRadixTrie()

        trie._root.children = [("flower", TrieNode(42))]

        insert_term(trie, "flower", 20)

        node, _ = trie._get_node_by_term("flower")

        assert node.get_score() == 42 + 20

    def test_insert_subterm_entry_changes_word_end_status_and_entry_count(self):
        trie = PruningRadixTrie()

        insert_term(trie, "flower power", 140)
        insert_term(trie, "flower power 123", 40)

        assert trie.get_num_entries() == 2

        insert_term(trie, "flower", 20)

        node, _ = trie._get_node_by_term("flower")

        assert node.is_word_end is True
        assert trie.get_num_entries() == 3

    def test_insert_subterm_entry_moves_node_down_a_level(self):
        trie = PruningRadixTrie()

        insert_term(trie, "flower power", 140)

        node, level = trie._get_node_by_term("flower power")

        assert level == 0

        insert_term(trie, "flower", 42)

        node, level = trie._get_node_by_term("flower power")

        assert level == 1

    def test_structure(self):
        trie = PruningRadixTrie()

        insert_term(trie, "flower power", 20)
        insert_term(trie, "flower power 123", 140)
        insert_term(trie, "flowchart", 40)

        node, _ = trie._get_node_by_term("flow")

        assert node.is_word_end is False
        assert node.max_score_children == 140

        assert len(node.children) == 2
        # sorted by max_score_children desc
        assert node.children[0][0] == 'er power'
        assert node.children[1][0] == 'chart'
