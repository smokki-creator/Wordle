import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy import func

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
from models import GameResult, CustomWord  # noqa: E402

# Load Russian words dictionary
with open('static/data/russian_words.json', 'r', encoding='utf-8') as f:
    DEFAULT_WORDS = json.load(f)

def get_all_words():
    custom_words = [word.word for word in CustomWord.query.all()]
    return DEFAULT_WORDS + custom_words

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new-word')
def new_word():
    words = get_all_words()
    word = random.choice(words)
    return jsonify({'word': word})

@app.route('/api/check-word', methods=['POST'])
def check_word():
    guess = request.json.get('guess', '').lower()
    target = request.json.get('target', '').lower()
    attempts = request.json.get('attempts', 0)

    words = get_all_words()
    if len(guess) != 5:
        return jsonify({'error': 'Слово должно быть из 5 букв'})

    if guess not in words:
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

@app.route('/api/stats')
def get_stats():
    total_games = GameResult.query.count()
    if total_games == 0:
        return jsonify({
            'totalGames': 0,
            'winRate': 0,
            'averageAttempts': 0
        })

    wins = GameResult.query.filter_by(success=True).count()
    win_rate = round((wins / total_games) * 100, 1)

    avg_attempts = db.session.query(
        func.avg(GameResult.attempts)
    ).filter_by(success=True).scalar()

    return jsonify({
        'totalGames': total_games,
        'winRate': win_rate,
        'averageAttempts': round(avg_attempts if avg_attempts else 0, 1)
    })

@app.route('/api/custom-words', methods=['GET', 'POST'])
def manage_custom_words():
    if request.method == 'GET':
        words = [word.word for word in CustomWord.query.all()]
        return jsonify(words)

    word = request.json.get('word', '').lower()
    if not word or len(word) != 5:
        return jsonify({'error': 'Слово должно быть из 5 букв'}), 400

    if word in DEFAULT_WORDS:
        return jsonify({'error': 'Это слово уже есть в основном словаре'}), 400

    existing_word = CustomWord.query.filter_by(word=word).first()
    if existing_word:
        return jsonify({'error': 'Это слово уже добавлено'}), 400

    new_word = CustomWord(word=word)
    db.session.add(new_word)
    db.session.commit()
    return jsonify({'message': 'Слово успешно добавлено'})

@app.route('/api/custom-words/<word>', methods=['DELETE'])
def delete_custom_word(word):
    word_record = CustomWord.query.filter_by(word=word.lower()).first()
    if word_record:
        db.session.delete(word_record)
        db.session.commit()
        return jsonify({'message': 'Слово успешно удалено'})
    return jsonify({'error': 'Слово не найдено'}), 404

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)