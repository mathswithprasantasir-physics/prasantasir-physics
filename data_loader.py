import json
import os

def load_questions():
    """Load questions from questions.json file"""
    json_path = os.path.join(os.path.dirname(__file__), 'questions.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('questions', [])
    except FileNotFoundError:
        print("⚠️ questions.json file not found! Creating empty list...")
        return []
    except json.JSONDecodeError:
        print("⚠️ questions.json is not valid JSON! Creating empty list...")
        return []

def save_questions(questions):
    """Save questions to questions.json file"""
    json_path = os.path.join(os.path.dirname(__file__), 'questions.json')
    
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'questions': questions}, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Error saving questions: {e}")
        return False

def get_topics():
    """Get unique topics from questions"""
    questions = load_questions()
    topics = list(set([q.get('topic', 'Unknown') for q in questions]))
    return sorted(topics)
