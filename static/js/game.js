class WordleGame {
    constructor() {
        this.currentRow = 0;
        this.currentTile = 0;
        this.gameOver = false;
        this.targetWord = '';
        this.maxAttempts = 6;
        this.maxLetters = 5;
        
        this.initializeBoard();
        this.initializeKeyboard();
        this.fetchNewWord();
    }

    async fetchNewWord() {
        const response = await fetch('/api/new-word');
        const data = await response.json();
        this.targetWord = data.word;
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
            const key = e.key.toLowerCase();
            if (key === 'enter') {
                this.handleKeyPress('enter');
            } else if (key === 'backspace') {
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

    async checkWord() {
        if (this.currentTile !== this.maxLetters) return;

        const currentRowElement = document.querySelector(`#game-board .row:nth-child(${this.currentRow + 1})`);
        const guess = Array.from(currentRowElement.children)
            .map(tile => tile.textContent.toLowerCase())
            .join('');

        const response = await fetch('/api/check-word', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({guess, target: this.targetWord})
        });

        const data = await response.json();

        if (data.error) {
            this.showMessage(data.error, 'danger');
            currentRowElement.classList.add('shake');
            setTimeout(() => currentRowElement.classList.remove('shake'), 500);
            return;
        }

        this.updateTiles(data.result);

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

    showMessage(text, type) {
        const messageElement = document.getElementById('message');
        messageElement.textContent = text;
        messageElement.className = `alert alert-${type}`;
        messageElement.classList.remove('d-none');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new WordleGame();
});
