# Qualitative Extraction

The aim of this project can be summarized as follows:

Given a PDF document and an exhaustive list of (currently 263) atomic queries (queries that can be answered with a YES 
or NO), output a JSON file that contains the relevant query, the answer, the reasoning if answer is YES, and token usage
of the LLM. There are two crucial components to achieve with this model, 

(1) High recall for the relevant queries: when selecting the top k queries, ensure that all ground truth queries are
present within the k queries

(2) High accuracy with answering the k queries: all answers that can be answered with YES must be answered with a YES
and the rest with a NO.

Different embedding models (OpenAI text-embedding-3-large, text-embedding-3-small, and JinaAI embedding model) were also
compared.

This project is split into two folders:

1. Preprocessing
2. Qualitative Extraction

## ./preprocessing
This folder will contain packages that is used (for the time being) for preprocessing any input data. The files contained are:

- process_atomic_query.py - contains functionality to remove irrelevant information from atomic queries

## ./qualitative_extraction
This folder contains the main data and code for extracting qualitative information from given extracted PDF chunks. The files in this folder include,

- extraction.ipynb - the main notebook where extraction code is implemented. This file takes top k relevant atomic queries for
each page of a given PDF and prompts an LLM to answer the queries. The evaluation of both extraction of relevant queries and
answering of queries can be done as well. The code should be commented for understanding.

The folder also includes the following sub-folder(s):

- /testing - this folder contains the custom datasets created for testing the recall of the different embedding models
- /N6LEV9~G - this folder contains parsed data from a PDF. Parsing is done per page and each page has a JSON file
associated with it
- /output - the formatted output JSON file containing the LLM response for each k query is stored here