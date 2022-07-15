from typing import List, Tuple

from pypruningradixtrie.input.abstract_input_provider import AbstractInputProvider
from pypruningradixtrie.input.input import Input
from pypruningradixtrie.trie import PruningRadixTrie
from pypruningradixtrie.trie_node import TrieNode


def fill_trie_from_file(trie: PruningRadixTrie, path: str, input_provider: AbstractInputProvider):
    input: List[Input] = input_provider.read_input_data(path)

    def insert_term_with_defaults(term: str, score: float):
        insert_term(trie, term, score, trie._root, [])

    for entry in input:
        insert_term_with_defaults(entry.query, entry.score)


def update_max_scores(nodes: List[TrieNode], term_score: float):
    for node in nodes:
        if term_score > node.max_score_children:
            node.max_score_children = term_score


def insert_term(trie: PruningRadixTrie, term: str, term_score: float,
                parent_node: TrieNode = None, parents: List[TrieNode] = None):
    if parents is None:
        parents = []
    if parent_node is None:
        parent_node = trie._root

    parents.append(parent_node)

    shared_prefix_length: int = 0

    # test whether the new child shares a prefix with existing ones
    if parent_node.has_children():
        for j in range(0, len(parent_node.children)):
            entry: Tuple[str, TrieNode] = parent_node.children[j]
            key: str = entry[0]
            node: TrieNode = entry[1]

            shared_prefix_length += __calc_shared_prefix_len(term, key)

            if shared_prefix_length > 0:
                # term already in trie
                # existing: flower
                # new:      flower
                if shared_prefix_length == len(term) and shared_prefix_length == len(key):
                    if node.get_score() == 0:
                        trie._term_count += 1

                    node.add_to_score(term_score)

                    update_max_scores(parents, node.get_score())

                # new term is substring of existing key -> new branch
                # existing: flower
                # new:      flow
                elif shared_prefix_length == len(term):
                    child: TrieNode = TrieNode(term_score)

                    child.children = [(key[shared_prefix_length:], node)]

                    child.max_score_children = max([node.get_score(), node.max_score_children])
                    update_max_scores(parents, term_score)

                    parent_node.replace_child(term[0:shared_prefix_length], child, index=j)

                    trie._term_count += 1

                # existing key is substring of new term -> term has to be added at lower level
                # existing: flower
                # new:      flower power
                elif shared_prefix_length == len(key):
                    insert_term(trie, term[shared_prefix_length:], term_score, node, parents)

                # new and existing term share a prefix, but have different suffixes
                # existing: flower
                # new:      flowchart
                else:
                    child: TrieNode = TrieNode(0)
                    child.children = [
                        (key[shared_prefix_length:], node),
                        (term[shared_prefix_length:], TrieNode(term_score))
                    ]

                    child.max_score_children = max(node.max_score_children, term_score, node.get_score())

                    update_max_scores(parents, term_score)

                    parent_node.replace_child(term[0:shared_prefix_length], child, index=j)

                    trie._term_count += 1

                return

    # parent had no children, just add the new term
    parent_node.add_child(term, TrieNode(term_score))

    trie._term_count += 1

    update_max_scores(parents, term_score)


def __calc_shared_prefix_len(term1: str, term2: str) -> int:
    len_shared: int = 0

    for i in range(0, min(len(term1), len(term2))):
        if term1[i] == term2[i]:
            len_shared = i + 1
        else:
            break

    return len_shared
