# Dev speak

_Dev speak_ analyzes year reports from development organizations and measures the amount of buzz-words used in each of them.
This is a first version that is very rough around the edges. The count needs to be heavily improved and results are simply dumped in separate JSON files at the moment.

## Usage

```python dev-speak.py```

Requires the following files:

1. __buzzwords.csv__  
An overview of the words that will be indexed.
2. __reports.csv__  
A list with organizations and year reports that will be analyzed.
