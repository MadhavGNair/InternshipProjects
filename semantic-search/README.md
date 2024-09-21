# Semantic Search

**Author: Madhav Girish Nair (nairm@cneutral.io)**

This project has two parts: (1) generating embeddings (2) extracting queries. The folder structure and files are organized based on the two parts and is explained below,

## ./data/
This folder contains the raw data for which embeddings must be created. In order to create embeddings, add files you want to embed into this folder. Currently, the following files are present,

- *atomic_factors.txt* - contains all 263 atomic queries, each in a new line
- *processed_output.json* - contains a list of 20 dictionary of data. The format is elaborate, but the relevant keys are 'text' and 'ground_truth'.

## ./embeddings/
All embeddings are stored in this folder. This avoids compute costs and time for generating embeddings every time. Remember to save all generated embeddings. The folder contains sub-folders in the following structure,

- /openai - contains all embeddings generating using OpenAI's text-embedding-3-small model.
- /large_openai - contains embeddings generated using OpenAI's text-embedding-3-large model.
- /jinaai - contains embeddings generated using JinaAI's jina-embeddings-v2-base-en model.
- /bert - contains embeddings generated using BERT's distilbert-base-nli-mean-tokens model.
- /sentence_embeddings - contains embeddings generated using OpenAI's text-embedding-3-small model for sentences.
- /sentence_embeddings_large - contains embeddings generated using OpenAI's text-embedding-3-large model for sentences.

Once more models are tested, more folders and sub-folders will be added.

## ./misc/
Outputs or files that are required for reference but not part of the pipeline are placed here. This folder can be considered as junk.

#### ./recall_scores.txt
This file is used to store the recall scores for all different models over different similarity functions for each page and set of queries.

#### ./mean_similarity.csv
This file contains the similarity of queries (columns) to pages (rows) averaged over all four embedding models.

## ./model_predictions/
All indices predicted by the different models are stored as pkl files here.

## ./generate_embeddings.py
This file is used to generate the embeddings. Remember to comment out the line that calls the API after use to avoid accidental calling.

## ./generate_sentence_embeddings.py
This file generates embeddings, but instead of iterating over pages, it iterates over chunks extracted from each page. Where the file ./generate_embeddings.py outputs a list of 21 lists of page embeddings, this file outputs a list of 21 lists of lists of sentence chunk embeddings. Note that each does does not necessarily correspond to one sentence.

## ./extract_queries.py
This file is used to extract the top *k* most similar queries for a given text. Recall testing is also done in this file, so this file can be used to print out or store the recall values as well.

## ./extract_sentence_queries.py
This file has the same functionality as ./extract_queries.py, but uses the output from ./generate_sentence_embeddings.py. Recall is moved to testing.py since the computation of indices takes slightly longer.

## ./testing.py
This file is used to read the indices of top similar queries predicted by the model and compute the recall. 

## ./page_based_extraction.py
This file is similar to extract_queries.py but instead of computing the top *k* most similar queries to each page, it compute the top *k* pages most similar to each query.

## ./ground_truth_indices.pkl
The pkl file that stores the ground truth indices.

## ./top_pred_indices.pkl
This file contains the predicted indices of queries using the sentence chunking method. Saved as computing indices takes a while.