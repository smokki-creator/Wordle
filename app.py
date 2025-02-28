import os
import json
import random
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Load Russian words dictionary
with open('static/data/russian_words.json', 'r', encoding='utf-8') as f:
    WORDS = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-word')
def new_word():
    # Return a random 5-letter word from the dictionary
    word = random.choice(WORDS)
    return jsonify({'word': word})

@app.route('/api/check-word', methods=['POST'])
def check_word():
    guess = request.json.get('guess', '').lower()
    target = request.json.get('target', '').lower()
    
    if len(guess) != 5:
        return jsonify({'error': 'Слово должно быть из 5 букв'})
        
    if guess not in WORDS:
        return jsonify({'error': 'Слово не найдено в словаре'})
    
    result = []
    target_letters = list(target)
    
    # First pass: mark correct letters (green)
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result.append('correct')
            target_letters[i] = None
        else:
            result.append('incorrect')
    
    # Second pass: mark present letters (yellow)
    for i, letter in enumerate(guess):
        if result[i] != 'correct' and letter in target_letters:
            result[i] = 'present'
            target_letters[target_letters.index(letter)] = None
            
    return jsonify({'result': result})
