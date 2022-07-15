from operator import attrgetter
from typing import List

from pypruningradixtrie.entry import Entry
from pypruningradixtrie.input.abstract_input_provider import AbstractInputProvider
from pypruningradixtrie.trie_node import TrieNode


def add_to_results(child_node: TrieNode, child_term: str,
                   prefix_string: str,
                   top_k: int,
                   results: List[Entry]):
    new_result: Entry = Entry(prefix_string + child_term, child_node.get_score())

    results.append(new_result)
    results.sort(key=attrgetter('score'), reverse=True)

    if len(results) > top_k:
        # we can just remove the last one because we only add one result at a time
        results.pop()


class PruningRadixTrie:
    _term_count: int
    _root: TrieNode

    def __init__(self, input_file_path: str = "", input_provider: AbstractInputProvider = None):
        """
        Crates a new PruningRadixTrie.
        Per default empty, use param for optional initialization with entries from file.

        :param input_file_path: path to a file to fill the trie from on creation
        :param input_provider: implementation of 'AbstractInputProvider' that should be used to read the given file
        """
        self._root = TrieNode(0)
        self._term_count = 0

        if input_file_path:
            if not input_provider:
                raise ValueError("You must provide an 'input_provider' if an 'input_file_path' is given")

            from pypruningradixtrie.insert import fill_trie_from_file

            fill_trie_from_file(self, input_file_path, input_provider)

    def get_num_entries(self) -> int:
        return self._term_count

    def get_top_k_for_prefix(self, prefix: str, top_k: int) -> List[Entry]:
        if top_k <= 0:
            return []

        results: List[Entry] = []

        self.__find_all_child_terms(prefix, self._root, top_k, "", results)

        return results

    def __find_all_child_terms(self,
                               prefix_to_restrict_children: str,
                               base_node: TrieNode,
                               top_k: int,
                               current_branch_term: str,
                               results: List[Entry]) -> None:
        """
        :param prefix_to_restrict_children: restrict the selection of child nodes, they have to match this prefix
        :param base_node: place where we continue to look for children
        :param top_k: number of results that we want
        :param current_branch_term: all prefixes that were collected on the branch up to this node
                (each node only knows its string (i.e. "ower") not the string(s) before it
                (i.e. "flow" & "er p" if the node is for "flower power").
                So we need the current_branch_term in order to be able to construct the whole result term)
        :param results: list of results that we want to return

        :return: no explicit return, modifies given 'results'-param  to collect all entries
                that were found with the given prefix, maximum amount: top_k
        """

        if self._should_skip_all_children_of_node(base_node, results, top_k):
            return

        should_not_restrict_children: bool = prefix_to_restrict_children == "" or prefix_to_restrict_children is None

        for child_term, child_node in base_node.children:

            if not self._should_skip_node_and_all_children(child_node, results, top_k):

                # looking for 'flow' and child is 'flower'
                # the child and all its children (i.e. 'flower power') are possible candidates
                if should_not_restrict_children or child_term.startswith(prefix_to_restrict_children):

                    if child_node.is_word_end:
                        add_to_results(child_node, child_term, current_branch_term, top_k, results)

                    if child_node.has_children():
                        # no restriction of children anymore because this node starts with the
                        # prefix that we entered
                        self.__find_all_child_terms(
                            prefix_to_restrict_children="",
                            base_node=child_node,
                            top_k=top_k,
                            current_branch_term=current_branch_term + child_term,
                            results=results)

                    # there is a prefix to restrict by and this child matched it
                    # => all other children cannot match, so skip them
                    if not should_not_restrict_children:
                        break

                # looking for 'flower power' and child is 'flower'
                # strip common prefix ('flower'), continue search with ' power' and current node as new root
                elif prefix_to_restrict_children.startswith(child_term):
                    if child_node.has_children():
                        # remove the current prefix of this node to create new prefix_to_restrict_children
                        # we look for 'flower power', this node is 'flower', only further restrict with ' power'
                        new_prefix_to_restrict_by: str = prefix_to_restrict_children[len(child_term):]

                        self.__find_all_child_terms(
                            prefix_to_restrict_children=new_prefix_to_restrict_by,
                            base_node=child_node,
                            top_k=top_k,
                            current_branch_term=current_branch_term + child_term,
                            results=results)

                    # the prefix to restrict by starts with this child
                    # => it cannot start with any other, so skip the other children
                    break

            # we want to skip this child node & it's children
            else:
                if should_not_restrict_children:
                    # we do not restrict the children, so check other child nodes if their score is high enough
                    # (NOTE: child nodes are sorted by their 'max_score_children' (not 'score'),
                    #       so it can happen that a 'later' child has a higher 'score' => we want to collect that)
                    continue
                else:
                    break

    def _should_skip_node_and_all_children(self, node: TrieNode, results: List[Entry], top_k: int) -> bool:
        """
        :param node: root of possible new branch to look through
        :param results: results that were already collected
        :param top_k: number of results that we want to collect

        :return: true if we should skip all children AND the score of this node is lower than the lowest in the results
                    => children & node cannot be not better than what we already have, so skip this whole branch
        """

        should_skip_all_children: bool = self._should_skip_all_children_of_node(node, results, top_k)
        if not should_skip_all_children:
            return False

        score_of_node_is_too_low: bool = node.get_score() <= results[top_k - 1].score

        return score_of_node_is_too_low

    @staticmethod
    def _should_skip_all_children_of_node(node: TrieNode, results: List[Entry], top_k: int) -> bool:
        """
        :param node: root of possible new branch to look through
        :param results: results that were already collected
        :param top_k: number of results that we want to collect

        :return: true if we have as many results as we want AND
                    all children of this node have a score lower than the lowest score in our results
                    => children can not be better than what we already have, so skip all of them
        """
        enough_results: bool = top_k == len(results)
        if not enough_results:
            return False

        score_of_all_children_is_too_low: bool = node.max_score_children <= results[top_k - 1].score

        return score_of_all_children_is_too_low

    # used for tests
    def _get_node_by_term(self, term: str, curr: TrieNode = None, level: int = 0) -> (TrieNode, int):
        """
        :param term: term to find
        :param curr: node where the search should start
        :param level: used to be able to return level where node was found. Should not be given on initial call

        :return: tuple of node & level where node was found or None if nothing was found
        """
        if not curr:
            curr = self._root

        if curr.has_children():
            for key, node in curr.children:
                if term == key:
                    return node, level

                if term.startswith(key):
                    if node.has_children() and len(node.children) > 0:
                        return self._get_node_by_term(term[len(key):], node, level + 1)
