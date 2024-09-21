import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm, trange
import matplotlib.pyplot as plt
from typing import List, Tuple
import json

# Step 1: Define the neural network architecture
class QuestionRetrievalModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(QuestionRetrievalModel, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.layer3 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.sigmoid(self.layer3(x))
        return x

# Step 2: Prepare the data
def prepare_data(page_embeddings, question_indices):
    X = torch.FloatTensor(page_embeddings)
    y = torch.zeros(len(page_embeddings), 263)
    for i, indices in enumerate(question_indices):
        y[i, indices] = 1
    return X, y

# Step 3: Split the data into training and validation sets
def split_data(X, y):
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train the model
def train_model(model, X_train, y_train, X_val, y_val, epochs=100, lr=0.001):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    # Create a tqdm progress bar for epochs
    epoch_bar = trange(epochs, desc="Training")
    
    # Lists to store losses for plotting
    train_losses = []
    val_losses = []

    for epoch in epoch_bar:
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val)
            val_loss = criterion(val_outputs, y_val)

        # Store losses
        train_losses.append(loss.item())
        val_losses.append(val_loss.item())

        # Update progress bar description with current losses
        epoch_bar.set_description(f"Train Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f}")

    # After training, print final losses
    print(f"Final Train Loss: {train_losses[-1]:.4f}, Final Val Loss: {val_losses[-1]:.4f}")

    return train_losses, val_losses

# Step 5: Inference function
def get_top_k_questions(model, page_embedding, k=5):
    model.eval()
    with torch.no_grad():
        output = model(torch.FloatTensor(page_embedding).unsqueeze(0))
    _, top_k_indices = torch.topk(output.squeeze(), k)
    return top_k_indices.tolist()

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

def load_queries(file_path: str) -> List[str]:
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [d.rstrip() for d in data]

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

# Main execution
if __name__ == "__main__":
    # Assume we have these variables:
    # page_embeddings: list of embeddings for 21 pages
    # question_indices: list of lists, where each sublist contains indices of relevant questions for a page
    # embedding_dim: dimension of the embeddings

    # Prepare the data
    # query_embeddings = np.load(f'./embeddings/{model}/query_embeddings_{model}.npy')
    page_embeddings = np.load(f'./embeddings/large_openai/pages_embeddings_large_openai.npy')
    all_queries = load_queries('./data/atomic_factors.txt')
    _, ground_truth = load_ground_truth('./data/processed_output.json')

    question_indices = extract_indices(all_queries, ground_truth)
    X, y = prepare_data(page_embeddings, question_indices)
    X_train, X_val, y_train, y_val = split_data(X, y)

    embedding_dim = len(page_embeddings[0])

    # Initialize and train the model
    model = QuestionRetrievalModel(input_size=embedding_dim, hidden_size=128, output_size=263)
    train_losses, val_losses = train_model(model, X_train, y_train, X_val, y_val)

    # Example inference
    sample_page_embedding = page_embeddings[0]  # Take the first page as an example
    top_30_questions = get_top_k_questions(model, sample_page_embedding, k=30)
    print(f"Predicted indices: {top_30_questions}")
    print(f'Actual indices: {question_indices[0]}')
    print(f'Recall = {compute_recall([question_indices[0]], [top_30_questions])}')

