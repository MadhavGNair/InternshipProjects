import os
import json
import numpy as np
import tensorflow_hub as hub
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load the Universal Sentence Encoder
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# OpenAI API setup
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure your API key is set in the environment

def load_chunks(directory):
    chunks = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            print(f"Loading file: {filepath}")
            with open(filepath, 'r') as file:
                try:
                    data = json.load(file)
                    if data["page_content"]:  # Ensure the page content is not empty
                        chunks.append(data["page_content"])
                    else:
                        print(f"Skipping file with empty page content: {filepath}")
                except json.JSONDecodeError as e:
                    print(f"Error loading JSON from file: {filepath} - {e}")
    return chunks

def load_all_chunks(root_directory):
    pdf_chunks = {}
    for subdir in os.listdir(root_directory):
        subdir_path = os.path.join(root_directory, subdir)
        print(f"Checking directory: {subdir_path}")
        if os.path.isdir(subdir_path):
            print(f"Loading chunks from: {subdir_path}")
            chunks = load_chunks(subdir_path)
            if chunks:
                pdf_chunks[subdir] = chunks
                print(f"Loaded {len(chunks)} chunks from {subdir_path}")
            else:
                print(f"No chunks found in {subdir_path}")
        else:
            print(f"{subdir_path} is not a directory")
    return pdf_chunks

def compute_embeddings(texts):
    print(f"Computing embeddings for {len(texts)} texts...")
    return embed(texts).numpy()

def rank_top_pairs(questions, chunks):
    question_embeddings = compute_embeddings(questions)
    chunk_embeddings = compute_embeddings(chunks)
    
    top_pairs = {}
    for i, question in enumerate(questions):
        similarities = cosine_similarity([question_embeddings[i]], chunk_embeddings)[0]
        print(f"Cosine similarities for question '{question}': {similarities}")
        top_indices = np.argsort(similarities)[-5:][::-1]
        top_pairs[question] = [(chunks[idx], similarities[idx]) for idx in top_indices if similarities[idx] >= 0.3]  # Lower threshold to 0.3 for testing
        print(f"Top pairs for question '{question}': {top_pairs[question]}")
    return top_pairs

def evaluate_with_llm(pairs):
    evaluated_pairs = {}
    llm = OpenAI(api_key=openai.api_key, model="gpt-4-o-mini")
    prompt_template = PromptTemplate(input_variables=["question", "chunk"], template="Question: {question}\n\nChunk: {chunk}\n\nAnswer:")
    llm_chain = LLMChain(llm=llm, prompt=prompt_template)

    for question, chunk_scores in pairs.items():
        evaluated_pairs[question] = []
        for chunk, score in chunk_scores:
            # Use LangChain to get the response
            response = llm_chain.run({"question": question, "chunk": chunk})
            response_text = response.strip()
            judgement = "yes" if "yes" in response_text.lower() else "no"
            reasoning = response_text
            evaluated_pairs[question].append((chunk, score, judgement, reasoning))
            print(f"Evaluation for question '{question}' with chunk: {judgement} - {reasoning}")
    return evaluated_pairs

def generate_score_vector(evaluated_pairs, num_questions):
    score_vector = [0] * num_questions
    for i, (question, evaluations) in enumerate(evaluated_pairs.items()):
        if any(judgement == "yes" for _, _, judgement, _ in evaluations):
            score_vector[i] = 1
    return score_vector

def generate_matrix(evaluated_pairs, num_chunks):
    matrix = []
    for question, evaluations in evaluated_pairs.items():
        row = [""] * num_chunks
        for chunk, score, judgement, reasoning in evaluations:
            if judgement == "yes":
                row.append(reasoning)
        matrix.append(row)
    return matrix

def generate_csv(matrix, filename):
    df = pd.DataFrame(matrix)
    df.to_csv(filename, index=False)

root_directory = "C:/Users/bryan/Desktop/answer/1"  # Path to the directory containing PDF folders
output_csv = "output.csv"  

questions = [
"Does the company have a publicly disclosed climate change policy?",
"Does the company integrate climate change considerations into its business strategy?",
"Has the company set targets for reducing greenhouse gas emissions?",
"Does the company disclose its strategy for achieving these targets?",
"Does the company consider climate change risks and opportunities in its business planning?",
"Has the company assessed the potential impact of climate change on its operations, supply chain, and markets?",
"Does the company consider the transition to a low-carbon economy in its strategic decisions?",
"Has the company identified and pursued business opportunities arising from the transition to a low-carbon economy?",
"Does the company identify climate-related risks and incorporate them into its risk management framework?",
"Does the company conduct scenario analysis to assess the impact of different climate change scenarios on its business?",
"Does the company have a plan to mitigate physical risks associated with climate change, such as extreme weather events?",
"Does the company engage with suppliers to manage climate-related risks in its supply chain?",
"Does the company incorporate climate-related risks into its investment planning and decision-making processes?",
"Does the company regularly review and update its climate risk management practices?",
"Does the company disclose its greenhouse gas emissions, including Scope 1, Scope 2, and, where relevant, Scope 3 emissions?",
"Does the company disclose its climate-related targets and progress towards achieving them?",
"Does the company report on its climate-related risks, opportunities, and financial impacts?",
"Does the company align its climate disclosures with internationally recognized reporting frameworks, such as the Task Force on Climate-related Financial Disclosures (TCFD)?",
"Does the company disclose its energy consumption and efficiency measures?",
"Does the company disclose its renewable energy usage and investments?",
"Does the company engage with policymakers and industry groups to support climate-related regulations and standards?",
"Does the company collaborate with stakeholders, including investors, customers, and suppliers, on climate-related initiatives?",
"Does the company participate in climate-related initiatives and alliances, such as the Science Based Targets initiative or the Carbon Disclosure Project (CDP)?",
"Does the company support and invest in research and development for low-carbon technologies and solutions?",
]

# Main process
pdf_chunks = load_all_chunks(root_directory)
print(f"Loaded chunks from {len(pdf_chunks)} PDFs.")

for pdf_name, chunks in pdf_chunks.items():
    print(f"Processing PDF: {pdf_name} with {len(chunks)} chunks.")
    top_pairs = rank_top_pairs(questions, chunks)
    evaluated_pairs = evaluate_with_llm(top_pairs)
    
    score_vector = generate_score_vector(evaluated_pairs, len(questions))
    matrix = generate_matrix(evaluated_pairs, len(chunks))
    
    # Output files
    pdf_output_csv = f"{pdf_name}_output.csv"  # Output CSV file name for each PDF
    generate_csv(matrix, pdf_output_csv)
    print(f"Score Vector for {pdf_name}: {score_vector}")
    print(f"Results saved to {pdf_output_csv}")
