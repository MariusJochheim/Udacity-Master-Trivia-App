import os
from pathlib import Path
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / '.env')

database_name = os.environ.get('TRIVIA_DB_NAME', 'trivia')
database_user = os.environ.get('TRIVIA_DB_USER', 'postgres')
database_password = os.environ.get('TRIVIA_DB_PASSWORD', 'password')
database_host = os.environ.get('TRIVIA_DB_HOST', 'localhost:5432')
database_path = os.environ.get(
    'DATABASE_URL',
    (
        f'postgresql://{database_user}:{database_password}'
        f'@{database_host}/{database_name}'
    )
)

if database_path.startswith('postgres://'):
    database_path = database_path.replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""


def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

"""
Question
"""


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = int(category)
        self.difficulty = int(difficulty)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': str(self.category),
            'difficulty': self.difficulty
        }

"""
Category
"""


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
