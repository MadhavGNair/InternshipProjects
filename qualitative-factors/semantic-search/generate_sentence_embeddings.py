'''
TO-DO:
- Load both pages and queries as lists
    - Give each query an id index
- Convert every element of each list to embeddings
    - Try different models
    - Save each embedding to file for reuse
    - Try to store embeddings in the same format for all models
'''
from typing import List, Tuple
import json
import openai
import glob
import pickle
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

def write_to_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def load_queries(file_path: str) -> List[str]:
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [d.rstrip() for d in data]

def load_ground_truth(file_path: str) -> Tuple[List[str], List[List[str]]]:
    json_text = []
    json_gt = []
    with open(file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            json_text.append(item['text'])
            json_gt.append([i.rstrip() for i in item['ground_truth']])
    return json_text, json_gt

def extract_indices(queries: List[str], gt: List[List[str]]) -> List[List[str]]:
    gt_indices = []
    for t in gt:
        indices = []
        for q in t:
            indices.append(queries.index(q))
        gt_indices.append(indices)
    return gt_indices

def generate_embeddings_openai(input: List[str], filename: str, model="text-embedding-3-small") -> Tuple[List[List[float]], int]:
    OPENAI_API_KEY = "API KEY HERE"

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    embeddings_response = client.embeddings.create(
        input=input,
        model=model
    )

    # extract embeddings
    embeddings = [item.embedding for item in embeddings_response.data]

    np.save(filename, embeddings)
    print(f'Embeddings written to file {filename}')

    # store token counts
    token_count = embeddings_response.usage.prompt_tokens
    return embeddings, token_count

def generate_embeddings_jinaai(input: List[str], filename: str) -> None:
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer API KEY HERE"
    }

    data = {
        "model": "jina-embeddings-v2-base-en",
        "embedding_type": "float",
        "input": input
    }

    url = "https://api.jina.ai/v1/embeddings"
    response = requests.post(url, headers=headers, json=data)

    write_to_json(response.json(), 'response_buffer.json')

    embeddings = [item['embedding'] for item in response.json()['data']]

    write_to_json(embeddings, filename)
    print(f'Embeddings written to file {filename}')

def generate_embeddings_bert(input: List[str], filename: str) -> None:
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    embeddings = model.encode(input)
    write_to_json(embeddings, filename)
    print(f'Embeddings written to file {filename}')


all_queries = load_queries('./data/atomic_factors.txt')
all_pages, ground_truth_queries = load_ground_truth('./data/processed_output.json')

# extract the indices of every ground truth query with relation to all the queries
ground_truth_indices = extract_indices(all_queries, ground_truth_queries)

# with open('./embeddings/sentence_embeddings/sentence_split_embeddings.pkl', 'rb') as f:
#     loaded_embeddings = pickle.load(f)

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )

all_split_pages = []

for text in all_pages:
    split_texts = [t.page_content for t in text_splitter.create_documents([text])]
    all_split_pages.append(split_texts)
    
all_embeddings = []
total_tokens = 0

# file_pattern = 'page_*_embeddings.json.npy'
# npy_files = sorted(glob.glob(file_pattern), key=lambda x: int(x.split('_')[1]))

# all_embeddings = [np.load(file) for file in npy_files]

# UNCOMMENT THE CODE CHUNK BELOW TO GENERATE EMBEDDINGS PER SENTENCE PER PAGE
# for idx, pages in enumerate(all_split_pages):
#     # generate embeddings for all chunks
#     embeddings, token_count = generate_embeddings_openai(pages, f'page_{idx}_embeddings_large', model="text-embedding-3-large")
#     all_embeddings.append(embeddings)
#     total_tokens += token_count

# with open('sentence_split_embeddings_large.pkl', 'wb') as f:
#     pickle.dump(all_embeddings, f)
# print(total_tokens)


