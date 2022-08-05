# PyPruningRadixTrie
![GitHub CI](https://github.com/otto-de/PyPruningRadixTrie/actions/workflows/pipeline.yml/badge.svg)
![PyPI version](https://badge.fury.io/py/pypruningradixtrie.svg)](https://badge.fury.io/py/pypruningradixtrie)

Python Port of [Pruning Radix Trie](https://github.com/wolfgarbe/PruningRadixTrie) by Wolf Garbe.

**Changes compared to original version**
* Removed parameter to disable pruning behavior.
  * See `test/non_pruning_radix_trie.py` for a non-pruning version that you can use to see the speed improvement.
* Added outline for more generic `InputProvider` and providers that read CSV or JSON as examples


## What and Why

A [**Trie**](https://en.wikipedia.org/wiki/Trie) is a tree data structure that is commonly used for searching terms
that start with a given prefix.  
It starts with an empty string at the base of the trie, the _root node_.        
Adding a new entry to the trie creates a new branch. This branch shares already present characters with existing nodes
and creates new nodes when it's prefix diverges from the present entries.
```text
# trie containing flower & flowchart (1 char = 1 node)

'' - f - l - o - w - e - r
                 |
                 c - h - a - r - t
```

A [**RadixTrie**](https://en.wikipedia.org/wiki/Radix_tree) is the space optimized version of a Trie.   
It combines the nodes with only one sub-node into one, containing more than one character.

```text
# radix trie containing flower & flowchart

'' - flow - er
      |
     chart
```

The prefix **Pruning** references the algorithm to query the RadixTrie.   
In order for the pruning to work, the nodes in RadixTrie are stored in a sorted manner.     
This structure allows **cutting off unpromising branches** during querying the trie which **makes the algorithm way faster**
compared to a non-pruning trie.


## Usage

**Create the PRT:**
```python
# empty trie
trie = PruningRadixTrie()

# fill with data from CSV file on creation
trie = PruningRadixTrie('./test_data.csv', CSVInputProvider(',', lambda x: float(x[1])))
```

**Add entries:**    
CSV:
```python
# fill with data from CSV file, score is at position 1, term at position 0
fill_trie_from_file(trie, './test_data.csv', CSVInputProvider(',', lambda x: float(x[1]), 0))
```

JSON:
```python
# define a functon to calculate the score out of a JSON entry
def score_fun(json_entry: Dict[str, Any]) -> float:
  return json_entry["pages"] * json_entry["year"] / 10.0

# "title" = key for term to insert into PRT
fill_trie_from_file(trie, './test_data.json', JSONInputProvider("title", score_fun))
```

Single Entry:
```python
# insert single entry
insert_term(trie, term="flower", score=20)
```

**Use the PRT:**
```python
# get the top 10 entries that start with 'flower'
trie.get_top_k_for_prefix('flower', 10)
```
