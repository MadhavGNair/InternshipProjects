'''
TO-DO:
- Use similarity computations to extract top k most similar queries to a given text
- Store the results in the following format
    - as a list of indices where the index of the list corresponds to each page
'''

import json
from typing import List, Tuple
import numpy as np
import pickle
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
        top_k_indices = np.argsort(similarities)[-top_k:][::-1].tolist()
        result.append(top_k_indices[0])
    
    return result

def generate_matrix(query_embeddings, sentence_embeddings):
    results = []
    
    for query in query_embeddings:
        similarities = []
        
        for page_idx, page_sentences in enumerate(sentence_embeddings):
            page_similarities = cosine_similarity([query], page_sentences)[0]
            similarities.append(page_similarities)
        results.append(similarities)
    return results

def top_k_queries_per_page(page_list, k):
    sorted_list = sorted(page_list, key=lambda x: x[1], reverse=True)
    result = [item[0] for item in sorted_list[:k]]
    
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

    return [round(recall, 2) for recall in recalls]

all_queries = load_queries('./data/atomic_factors.txt')
_, ground_truth = load_ground_truth('./data/processed_output.json')

# extract the indices of every ground truth query with relation to all the queries
ground_truth_indices = extract_indices(all_queries, ground_truth)

# similarity_funcs = ['cosine', 'euclidean', 'manhattan', 'dot_product', 'jaccard']
models = ['large_openai', 'openai']
mode = ['large', 'small']
selected_idx = 0

query_embeddings = np.load(f'./embeddings/{models[selected_idx]}/query_embeddings_{models[selected_idx]}.npy')
with open(f'./embeddings/sentence_embeddings_{mode[selected_idx]}/sentence_split_embeddings_{mode[selected_idx]}.pkl', 'rb') as f:
    pages_embeddings = pickle.load(f)

most_similar_queries = []

# TEST 1: FOR EACH SENTENCE, GET TOP QUERY
for sentence_embeddings in pages_embeddings:
    top_index = top_k_similar_queries(sentence_embeddings, query_embeddings, 1, 'cosine')
    most_similar_queries.append(top_index)

most_similar_queries = [list(set(i)) for i in most_similar_queries]

# save predicted indices as computing takes a while
# with open('top_k_indices_small.pkl', 'wb') as f:
#     pickle.dump(most_similar_queries, f)

# predicted indices saved as top_pred_indices.pkl. If file exitst, no need to run this file.

# TEST 2: FOR EACH QUERY, GET TOP SENTENCE
# similarity_matrix = generate_matrix(query_embeddings, pages_embeddings)

# pages = [[] for _ in range(21)]

# for q_idx, query in enumerate(similarity_matrix):
#     for p_idx, page in enumerate(query):
#         pages[p_idx].append((q_idx, max(page)))

# final_indices = []
# for page in pages:
#     final_indices.append(top_k_queries_per_page(page, 30))

# RECALL COMPUTATION
# recall = compute_recall(ground_truth_indices, most_similar_queries)
# print(recall)
# print(f'Mean: {np.mean(np.array(recall))}')
# print(f'Average k={np.mean([len(i) for i in most_similar_queries])}')
# print(f'k per page={[len(i) for i in most_similar_queries]}')
'''
RESULT FOR TEST 1:
[1.0, 1.0, 0.8, 1.0, 1.0, 1.0, 1.0, 0.78, 0.8, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.82, 0.88, 1.0, 1.0]
Mean: 0.9561904761904761
Average k=24.333333333333332
k per page=[20, 21, 23, 27, 25, 21, 22, 26, 27, 23, 22, 26, 25, 31, 25, 27, 24, 23, 22, 21, 30]

RESULT FOR TEST 2:
[1.0, 1.0, 0.8, 1.0, 1.0, 1.0, 1.0, 0.78, 0.8, 1.0, 1.0, 0.83, 1.0, 0.88, 1.0, 1.0, 1.0, 0.82, 0.88, 0.88, 0.88]
Mean: 0.9309523809523809
Average k=30.0
k per page=[30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30]
'''



