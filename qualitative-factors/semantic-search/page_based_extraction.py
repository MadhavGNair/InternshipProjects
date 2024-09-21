import pandas as pd
import numpy as np
import json
from typing import List, Tuple

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

def reorganize_rankings(rankings, num_pages=21):
    result = [[] for _ in range(num_pages)]
    for question, page_rankings in enumerate(zip(*rankings)):
        for page in set(page_rankings):
            result[page].append(question)
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

def process_similarities_pandas(k):
    df = pd.read_csv('./mean_similarity.csv', index_col=0)
    
    top_k_indices = df.apply(lambda col: col.nlargest(k).index.tolist(), axis=0)

    return top_k_indices

k = 7
questions_per_page = process_similarities_pandas(k)

all_queries = load_queries('./data/atomic_factors.txt')
_, ground_truth = load_ground_truth('./data/processed_output.json')
ground_truth_indices = extract_indices(all_queries, ground_truth)

row_list = [questions_per_page.iloc[i].tolist() for i in range(k)]

# for each page, all questions that picked that page in its top k
pages_pred = reorganize_rankings(row_list, num_pages=21)

recall = compute_recall(ground_truth_indices, pages_pred)

print(recall)
print(f'mean recall: {np.mean(np.array(recall))}')

