import os
import json

def read_questions(file_path):
    with open(file_path, 'r') as file:
        return [line.strip().strip('"') for line in file if line.strip()]

def create_json_from_txt_files(folder_path):
    result = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            questions = read_questions(file_path)
            result[filename] = questions
    
    return result

def concatenate_factors(folder_path, output_file='output.json'):
    json_data = create_json_from_txt_files(folder_path)
    
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)
    
    print("JSON file created successfully.")

