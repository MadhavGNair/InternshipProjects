import hashlib

def load_queries(file_path):
    with open(file_path, 'r') as file:
        data = file.readlines()
    return [d.rstrip() for d in data]

def generate_question_ids(questions, topic_ids, subtopic_ids):
    if isinstance(questions, str):
        questions = [questions]
        topic_ids = [topic_ids]
        subtopic_ids = [subtopic_ids]
    
    def create_id(question, topic, subtopic):
        # Create a hash of the full question
        hash_object = hashlib.md5(question.encode())
        hash_str = hash_object.hexdigest()[:6]
        
        return f"{topic}_{subtopic}_{hash_str}"

    return [create_id(q, t, s) for q, t, s in zip(questions, topic_ids, subtopic_ids)]

all_queries = load_queries('./data/atomic_factors.txt')


