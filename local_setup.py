
"""
Скрипт для экспорта игры Квордли для локального использования
"""
import os
import shutil
import sys

def create_local_version():
    # Создаем директорию для локальной версии
    local_dir = "quordle_local"
    os.makedirs(local_dir, exist_ok=True)
    
    # Копируем необходимые файлы и директории
    dirs_to_copy = ["static", "templates"]
    files_to_copy = ["app.py", "main.py", "models.py"]
    
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(local_dir, dir_name), dirs_exist_ok=True)
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, os.path.join(local_dir, file_name))
    
    # Создаем файл требований
    with open(os.path.join(local_dir, "requirements.txt"), "w") as f:
        f.write("flask\nflask-sqlalchemy\nsqlalchemy\nemail-validator\npsycopg2-binary\ngunicorn\n")
    
    # Создаем локальную версию app.py без PostgreSQL
    create_local_app_py(local_dir)
    
    # Создаем инструкции по запуску
    create_readme(local_dir)
    
    print(f"Локальная версия игры создана в директории '{local_dir}'")
    print("Следуйте инструкциям в README.md для запуска игры")

def create_local_app_py(local_dir):
    """Создает упрощенную версию app.py с использованием SQLite вместо PostgreSQL"""
    with open(os.path.join(local_dir, "app.py"), "w") as f:
        f.write("""import os
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

# Используем SQLite вместо PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quordle.db"
app.secret_key = "default-secret-key"

db.init_app(app)

# Импортируем модели после инициализации db
from models import GameResult, CustomWord  # noqa: E402

# Загружаем словарь русских слов
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

    # Первый проход: отметить правильные буквы (зеленые)
    for i, letter in enumerate(guess):
        if letter == target[i]:
            result.append('correct')
            target_letters[i] = None
        else:
            result.append('incorrect')

    # Второй проход: отметить присутствующие буквы (желтые)
    for i, letter in enumerate(guess):
        if result[i] != 'correct' and letter in target_letters:
            result[i] = 'present'
            target_letters[target_letters.index(letter)] = None

    # Сохраняем результат игры, если слово угадано или достигнуто максимальное число попыток
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

# Создаем таблицы
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
""")

def create_readme(local_dir):
    """Создает файл README.md с инструкциями по установке и запуску"""
    with open(os.path.join(local_dir, "README.md"), "w") as f:
        f.write("""# Квордли - локальная версия

## Установка

1. Убедитесь, что у вас установлен Python 3.11 или выше
2. Откройте командную строку/терминал в этой папке
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

## Запуск игры

1. В командной строке/терминале выполните:
   ```
   python main.py
   ```
2. Откройте браузер и перейдите по адресу: `http://localhost:5000`

## Особенности локальной версии

- Игра использует локальную базу данных SQLite вместо PostgreSQL
- Все данные (статистика, пользовательские слова) хранятся локально
- Игра доступна только на вашем компьютере, когда запущен сервер

## Примечания

- Чтобы остановить сервер, нажмите Ctrl+C в командной строке/терминале
- База данных хранится в файле `quordle.db` в этой папке
""")

if __name__ == "__main__":
    create_local_version()
