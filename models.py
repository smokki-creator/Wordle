from datetime import datetime
from app import db

class GameResult(db.Model):
    __tablename__ = 'game_result'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), nullable=False)
    attempts = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'attempts': self.attempts,
            'success': self.success,
            'created_at': self.created_at.isoformat()
        }

class CustomWord(db.Model):
    __tablename__ = 'custom_word'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'created_at': self.created_at.isoformat()
        }