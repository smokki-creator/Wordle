import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

Base = declarative_base()

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

db.init_app(app)

# Import models after db initialization
from models import GameResult  # noqa: E402

# Load Russian words dictionary
with open('static/data/russian_words.json', 'r', encoding='utf-8') as f:
    WORDS = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-word')
def new_word():
    word = random.choice(WORDS)
    return jsonify({'word': word})

@app.route('/api/check-word', methods=['POST'])
def check_word():
    guess = request.json.get('guess', '').lower()
    target = request.json.get('target', '').lower()
    attempts = request.json.get('attempts', 0)

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

    # Save game result if word is guessed or max attempts reached
    if guess == target or attempts >= 5:
        game_result = GameResult(
            word=target,
            attempts=attempts + 1,
            success=guess == target
        )
        db.session.add(game_result)
        db.session.commit()

    return jsonify({'result': result})

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)