#!/usr/bin/env python3
"""
Adatbázis feltöltő script kvízkérdésekkel
"""

import sys
import os

# Hozzáadjuk a src könyvtárat a Python path-hoz
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from src.models.user import db
from src.models.game import QuizQuestion

# Flask app létrehozása
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Kvízkérdések listája
QUIZ_QUESTIONS = [
    {
        "question": "Hol volt az első randijuk?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "kapcsolat"
    },
    {
        "question": "Ki mondta ki először: 'Szeretlek'?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "kapcsolat"
    },
    {
        "question": "Mi a pár közös kedvenc sorozata?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "közös_érdeklődés"
    },
    {
        "question": "Hány gyereket terveznek?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "jövő"
    },
    {
        "question": "Melyikük a rendetlenebb otthon?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "személyiség"
    },
    {
        "question": "Mi volt a menyasszony jele az óvodában?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "múlt"
    },
    {
        "question": "Melyik a vőlegény kedvenc étele?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "személyiség"
    },
    {
        "question": "Hol töltötték az első közös nyaralásukat?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "kapcsolat"
    },
    {
        "question": "Ki főz jobban a párból?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "személyiség"
    },
    {
        "question": "Milyen állatot szeretnének tartani?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "jövő"
    },
    {
        "question": "Melyikük a korábbi kelő?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "személyiség"
    },
    {
        "question": "Mi a menyasszony kedvenc virága?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "személyiség"
    },
    {
        "question": "Hány éve ismerik egymást?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "kapcsolat"
    },
    {
        "question": "Melyik a közös kedvenc filmjük?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "közös_érdeklődés"
    },
    {
        "question": "Ki vezet jobban autót?",
        "answer": "Válasz az ifjú pártól függ",
        "category": "személyiség"
    }
]

def populate_quiz_questions():
    """Kvízkérdések feltöltése az adatbázisba"""
    with app.app_context():
        # Táblák létrehozása
        db.create_all()
        
        # Ellenőrizzük, hogy vannak-e már kérdések
        existing_count = QuizQuestion.query.count()
        
        if existing_count > 0:
            print(f"Az adatbázisban már van {existing_count} kvízkérdés.")
            return
        
        # Kérdések hozzáadása
        for q_data in QUIZ_QUESTIONS:
            question = QuizQuestion(
                question=q_data["question"],
                answer=q_data["answer"],
                category=q_data["category"]
            )
            db.session.add(question)
        
        try:
            db.session.commit()
            print(f"Sikeresen hozzáadva {len(QUIZ_QUESTIONS)} kvízkérdés az adatbázishoz.")
        except Exception as e:
            db.session.rollback()
            print(f"Hiba történt a kvízkérdések hozzáadása során: {e}")

if __name__ == "__main__":
    populate_quiz_questions()

