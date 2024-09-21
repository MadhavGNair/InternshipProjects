from typing import List, Tuple
import pickle
import json
import numpy as np

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

with open('./model_predictions/top_pred_indices_by_query_large.pkl', 'rb') as f:
    predicted_indices = pickle.load(f)

all_queries = load_queries('./data/atomic_factors.txt')
_, ground_truth = load_ground_truth('./data/processed_output.json')

# extract the indices of every ground truth query with relation to all the queries
ground_truth_indices = extract_indices(all_queries, ground_truth)

recall = compute_recall(ground_truth_indices, predicted_indices)

lengths = [len(i) for i in predicted_indices]

print(np.mean(np.array(lengths)))

print(recall)
print(round(np.mean(np.array(recall)), 2))
# print(ground_truth_indices[7])
# print(predicted_indices[7])

