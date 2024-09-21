'''
TO-DO:
- Use similarity computations to extract top k most similar queries to a given text
- Store the results in the following format
    - {"text_id": (int) id of the text, "query_ids": (List) a list of ids of the k most similar queries}
'''

import json
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import manhattan_distances

def load_queries(file_path: str) -> List[str]:
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [d.rstrip() for d in data]

def load_embedding(filepath: str) -> List[List[float]]:
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

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

def get_top_k_indices(row, k):
    return list(np.argsort(row)[-k:][::-1])

def compute_similarity(pages_embedding, query_embedding, similarity_func='cosine'):
    pages = np.array(pages_embedding)
    queries = np.array(query_embedding)

    # define similarity functions
    similarity_functions = {
        'cosine': lambda x, y: cosine_similarity(x.reshape(1, -1), y.reshape(1, -1))[0][0]
    }
    
    sim_func = similarity_functions.get(similarity_func)
    if sim_func is None:
        raise ValueError(f"Invalid similarity function: {similarity_func}")
    
    result = []
    for page in pages:
        similarities = [sim_func(page, query) for query in queries]
        result.append(similarities)
    
    return np.array(result)

def top_k_similar_queries(pages_embedding, query_embedding, top_k=5, similarity_func='cosine'):
    pages = np.array(pages_embedding)
    queries = np.array(query_embedding)

    # define similarity functions
    similarity_functions = {
        'cosine': lambda x, y: cosine_similarity(x.reshape(1, -1), y.reshape(1, -1))[0][0],
        'euclidean': lambda x, y: -euclidean_distances(x.reshape(1, -1), y.reshape(1, -1))[0][0],
        'manhattan': lambda x, y: -manhattan_distances(x.reshape(1, -1), y.reshape(1, -1))[0][0],
        'dot_product': lambda x, y: np.dot(x, y),
        'jaccard': lambda x, y: np.sum(np.minimum(x, y)) / np.sum(np.maximum(x, y))
    }
    
    sim_func = similarity_functions.get(similarity_func)
    if sim_func is None:
        raise ValueError(f"Invalid similarity function: {similarity_func}")
    
    result = []
    for page in pages:
        similarities = [sim_func(page, query) for query in queries]
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]
        result.append(top_k_indices.tolist())
    
    return result

def compute_recall(ground_truth, pred_indices):
    recalls = []
    for gt, pred in zip(ground_truth, pred_indices):
        gt_set = set(gt)
        pred_set = set(pred)
        
        true_positives = len(gt_set.intersection(pred_set))
        total_relevant = len(gt_set)
        
        if total_relevant == 0:
            recall = None
        else:
            recall = true_positives / total_relevant
        
        recalls.append(recall)

    return np.array([round(recall, 2) for recall in recalls])

all_queries = load_queries('./data/atomic_factors.txt')
_, ground_truth = load_ground_truth('./data/processed_output.json')

# extract the indices of every ground truth query with relation to all the queries
ground_truth_indices = extract_indices(all_queries, ground_truth)
similarity_funcs = ['cosine', 'euclidean', 'manhattan', 'dot_product', 'jaccard']
models = ['large_openai', 'openai', 'jinaai', 'bert']

sorted = False
for model in models:
    query_embeddings = np.load(f'./embeddings/{model}/query_embeddings_{model}.npy')
    pages_embeddings = np.load(f'./embeddings/{model}/pages_embeddings_{model}.npy')
    print(f'{model}:')
    for func in ['cosine']:
        top_indices = top_k_similar_queries(pages_embeddings, query_embeddings, 30, func)
        recall_list = compute_recall(ground_truth_indices, top_indices)
        if sorted:
            print(f'{func}: {sorted(recall_list, reverse=True)}\n')
            print(f'Mean recall = {round(np.mean(np.array(recall_list)), 2)}')
            print(f'Worst page = {np.argmin(np.array(recall_list))}')
        else:
            print(f'{func}: {recall_list}')
            print(f'Mean recall = {round(np.mean(np.array(recall_list)), 2)}')
            print(f'Worst page = {np.argmin(np.array(recall_list))}')
    print()



