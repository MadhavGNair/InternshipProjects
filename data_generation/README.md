# Semantic Search
**Author: Madhav Girish Nair (madhavgirish02@gmail.com)**

The goal of this project is split into two parts:

1. Synthesizing data - creating custom dataset from atomic queries
2. Query extraction - extracting the top *k* most similar queries from a given list based on given text

The files and folders are explained below,

## ./data_generation
This folder contains the data and code required for the entire project.

### /atomic_factors
This folder contains the raw data, namely the atomic queries. The three relevant files from this folder are,

- /atomic_factors.json - atomic queries split by topics from Norges Bank publications
- /atomic_factors.txt - all atomic queries without any grouping
- /ESG_factors.json - all atomic queries split by topics from Norges Bank publications and further split by ESG

### /extensions
This folder contains all modules used in the project. The relevant files are,

- /concat_atomic_factors.py - contains function used to extract, process, and save atomic factors

### /junk
This folder contains all junk. All outputs that were relevant at some point are stored here. The files are mainly used to keep track of formatting and testing.

### /output
This folder contains the most recent and relevant outputs. Used for storage for later processing and moved to /junk or deleted once redundant.

### /sythesize_data.ipynb
This file is the main notebook used for synthesizing data. The instructions to run the code should be found within the code itself.

### /query_extraction.ipynb
This file is the main notebook used for similarity functionality and extracting top *k* most similar queries given a text.