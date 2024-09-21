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
import requests
from sentence_transformers import SentenceTransformer
import numpy as np

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

def generate_embeddings_openai(input: List[str], filename: str, model="text-embedding-3-small") -> int:
    OPENAI_API_KEY = "API KEY HERE"

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    embeddings_response = client.embeddings.create(
        input=input,
        model=model
    )

    # extract embeddings
    embeddings = [item.embedding for item in embeddings_response.data]

    write_to_json(embeddings, filename)
    print(f'Embeddings written to file {filename}')
    # store token counts
    token_count = embeddings_response.usage.prompt_tokens
    return token_count

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

# uncomment the following lines and change first param to desired input to generate OpenAI embeddings
# num_tokens = generate_embeddings_openai(all_queries, 'query_embeddings_large_openai.json', "text-embedding-3-large")
# print(num_tokens)

# uncomment the following lines and change first param to desired input to generate JinaAI embeddings
# generate_embeddings_jinaai(all_queries, 'query_embeddings_jinaai.json')

# uncomment the following lines and change first param to desired input to generate BERT embeddings
# generate_embeddings_jinaai(all_pages, 'pages_embeddings_bert.json')

