class WordleGame {
    constructor() {
        this.currentRow = 0;
        this.currentTile = 0;
        this.gameOver = false;
        this.targetWord = '';
        this.maxAttempts = 6;
        this.maxLetters = 5;
        this.letterStates = {};

        this.mainMenu = document.getElementById('mainMenu');
        this.gameSection = document.getElementById('gameSection');

        this.initializeUI();
        this.initializeBoard();
        this.initializeKeyboard();
    }

    initializeUI() {
        // Инициализация кнопок главного меню
        document.getElementById('playButton').addEventListener('click', () => {
            this.startNewGame();
        });

        document.getElementById('statsButton').addEventListener('click', () => {
            this.showStats();
        });

        document.getElementById('wordsButton').addEventListener('click', () => {
            this.showWordsManager();
        });

        // Кнопка возврата в меню
        document.getElementById('backToMenu').addEventListener('click', () => {
            this.gameSection.classList.add('d-none');
            this.mainMenu.classList.remove('d-none');
        });

        // Форма добавления слов
        document.getElementById('addWordForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addCustomWord();
        });
    }

    async startNewGame() {
        this.resetGame();
        await this.fetchNewWord();
        this.mainMenu.classList.add('d-none');
        this.gameSection.classList.remove('d-none');
        document.getElementById('message').classList.add('d-none');
    }

    resetGame() {
        this.currentRow = 0;
        this.currentTile = 0;
        this.gameOver = false;
        this.letterStates = {};

        // Очистка игрового поля
        document.querySelectorAll('.tile').forEach(tile => {
            tile.textContent = '';
            tile.className = 'tile';
        });

        // Сброс цветов клавиатуры
        document.querySelectorAll('.keyboard button').forEach(button => {
            if (button.getAttribute('data-key') !== 'enter' && 
                button.getAttribute('data-key') !== 'backspace') {
                button.className = '';
            }
        });
    }

    async fetchNewWord() {
        const response = await fetch('/api/new-word');
        const data = await response.json();
        this.targetWord = data.word;
    }

    async showStats() {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        const statsContent = document.getElementById('statsContent');

        let html = `
            <div class="stats-container">
                <div class="text-center mb-3">
                    <h3 class="display-4">${stats.totalGames}</h3>
                    <p class="mb-0">Всего игр</p>
                </div>
                <div class="text-center mb-3">
                    <h3 class="display-4">${stats.winRate}%</h3>
                    <p class="mb-0">Процент побед</p>
                </div>
                <div class="text-center">
                    <h3 class="display-4">${stats.averageAttempts}</h3>
                    <p class="mb-0">Среднее число попыток</p>
                </div>
            </div>
        `;

        statsContent.innerHTML = html;
        new bootstrap.Modal(document.getElementById('statsModal')).show();
    }

    async showWordsManager() {
        await this.loadCustomWords();
        new bootstrap.Modal(document.getElementById('wordsModal')).show();
    }

    async loadCustomWords() {
        const response = await fetch('/api/custom-words');
        const words = await response.json();
        const wordsList = document.getElementById('customWordsList');

        if (words.length === 0) {
            wordsList.innerHTML = '<div class="text-center text-muted">Пока нет добавленных слов</div>';
            return;
        }

        wordsList.innerHTML = words.map(word => `
            <div class="custom-word-item">
                <span class="fw-bold">${word.toUpperCase()}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="game.deleteCustomWord('${word}')">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `).join('');
    }

    async addCustomWord() {
        const input = document.getElementById('newWord');
        const word = input.value.toLowerCase();

        if (!/^[а-яё]{5}$/.test(word)) {
            this.showMessage('Слово должно состоять из 5 русских букв', 'danger');
            return;
        }

        const response = await fetch('/api/custom-words', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({word})
        });

        if (response.ok) {
            input.value = '';
            await this.loadCustomWords();
            this.showMessage('Слово успешно добавлено', 'success', 'wordsModal');
        } else {
            const data = await response.json();
            this.showMessage(data.error || 'Ошибка при добавлении слова', 'danger', 'wordsModal');
        }
    }

    async deleteCustomWord(word) {
        if (!confirm(`Удалить слово "${word.toUpperCase()}"?`)) {
            return;
        }

        const response = await fetch(`/api/custom-words/${word}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            await this.loadCustomWords();
            this.showMessage('Слово успешно удалено', 'success', 'wordsModal');
        } else {
            this.showMessage('Ошибка при удалении слова', 'danger', 'wordsModal');
        }
    }

    initializeBoard() {
        const board = document.getElementById('game-board');
        for (let i = 0; i < this.maxAttempts; i++) {
            const row = document.createElement('div');
            row.className = 'row';
            for (let j = 0; j < this.maxLetters; j++) {
                const tile = document.createElement('div');
                tile.className = 'tile';
                row.appendChild(tile);
            }
            board.appendChild(row);
        }
    }

    initializeKeyboard() {
        document.querySelectorAll('.keyboard button').forEach(button => {
            button.addEventListener('click', () => {
                const key = button.getAttribute('data-key');
                this.handleKeyPress(key);
            });
        });

        document.addEventListener('keydown', (e) => {
            let key = e.key.toLowerCase();
            if (key === 'enter') {
                this.handleKeyPress('enter');
            } else if (key === 'backspace' || key === 'delete') {
                this.handleKeyPress('backspace');
            } else if (/^[а-яё]$/.test(key)) {
                this.handleKeyPress(key);
            }
        });
    }

    handleKeyPress(key) {
        if (this.gameOver) return;

        if (key === 'enter') {
            this.checkWord();
        } else if (key === 'backspace') {
            this.deleteLetter();
        } else if (this.currentTile < this.maxLetters) {
            this.addLetter(key);
        }
    }

    addLetter(letter) {
        const currentRowElement = document.querySelector(`#game-board .row:nth-child(${this.currentRow + 1})`);
        const tile = currentRowElement.children[this.currentTile];
        tile.textContent = letter.toUpperCase();
        tile.classList.add('filled');
        this.currentTile++;
    }

    deleteLetter() {
        if (this.currentTile > 0) {
            this.currentTile--;
            const currentRowElement = document.querySelector(`#game-board .row:nth-child(${this.currentRow + 1})`);
            const tile = currentRowElement.children[this.currentTile];
            tile.textContent = '';
            tile.classList.remove('filled');
        }
    }

    updateKeyboardColors(guess, result) {
        const letters = guess.split('');
        letters.forEach((letter, index) => {
            const status = result[index];
            const currentState = this.letterStates[letter] || 'incorrect';
            if (status === 'correct' || (status === 'present' && currentState !== 'correct')) {
                this.letterStates[letter] = status;
            }
        });

        document.querySelectorAll('.keyboard button').forEach(button => {
            const key = button.getAttribute('data-key');
            if (key && key !== 'enter' && key !== 'backspace') {
                const state = this.letterStates[key] || '';
                button.className = '';
                if (state) {
                    button.classList.add(state);
                }
            }
        });
    }

    async checkWord() {
        if (this.currentTile !== this.maxLetters) return;

        const currentRowElement = document.querySelector(`#game-board .row:nth-child(${this.currentRow + 1})`);
        const guess = Array.from(currentRowElement.children)
            .map(tile => tile.textContent.toLowerCase())
            .join('');

        const response = await fetch('/api/check-word', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                guess,
                target: this.targetWord,
                attempts: this.currentRow
            })
        });

        const data = await response.json();

        if (data.error) {
            this.showMessage(data.error, 'danger');
            currentRowElement.classList.add('shake');
            setTimeout(() => currentRowElement.classList.remove('shake'), 500);
            return;
        }

        this.updateTiles(data.result);
        this.updateKeyboardColors(guess, data.result);

        if (guess === this.targetWord) {
            this.gameOver = true;
            this.showMessage('Поздравляем! Вы угадали слово!', 'success');
        } else if (this.currentRow === this.maxAttempts - 1) {
            this.gameOver = true;
            this.showMessage(`Игра окончена! Загаданное слово: ${this.targetWord.toUpperCase()}`, 'danger');
        } else {
            this.currentRow++;
            this.currentTile = 0;
        }
    }

    updateTiles(result) {
        const currentRowElement = document.querySelector(`#game-board .row:nth-child(${this.currentRow + 1})`);
        const tiles = currentRowElement.children;

        result.forEach((status, index) => {
            setTimeout(() => {
                tiles[index].classList.add(status);
            }, index * 100);
        });
    }

    showMessage(text, type, modalId = null) {
        if (modalId) {
            const modal = document.getElementById(modalId);
            const messageDiv = modal.querySelector('.alert') || document.createElement('div');
            messageDiv.className = `alert alert-${type} mt-3`;
            messageDiv.textContent = text;
            if (!modal.querySelector('.alert')) {
                modal.querySelector('.modal-body').appendChild(messageDiv);
            }
            setTimeout(() => messageDiv.remove(), 3000);
        } else {
            const messageElement = document.getElementById('message');
            messageElement.textContent = text;
            messageElement.className = `alert alert-${type}`;
            messageElement.classList.remove('d-none');
        }
    }
}

// Глобальная переменная для доступа к игре из обработчиков событий
let game;

document.addEventListener('DOMContentLoaded', () => {
    game = new WordleGame();
});