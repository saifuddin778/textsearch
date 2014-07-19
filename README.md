textsearch
==========
A minimalistic, fast and memory-efficient document lookup system in Python based on noun hashing technique.
####Usage:
```python
>>> from textsearch import textsearch
>>> t = textsearch(docs, histogram=False)
```
Here, `docs` can be provided in one of the two formats below:
* A list of strings i.e. `docs = ['saif went to beach', 'party at isloo was amazing', ...]`.
* A list of objects with each containing its respective id: `docs = [['1345', 'saif went to beach'], ['1363','party at isloo was amazing']...]`.
Setting the `histogram` option to true will create a histogram of words in the `docs`, which will help in a probablistic type of search (coming soon). Once the lookup table is created, documents can be searched as:
```python
>>> t.lookup('saif', individual=True/False)
>>> ['1345', 'saif went to beach']
```



####Dependencies:
* NLTK
* TextBlob

