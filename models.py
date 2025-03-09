from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialisation de SQLAlchemy
db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    token = db.Column(db.String(36), unique=True, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    # Un étudiant peut avoir une seule réponse (relation 1-1)
    reponse = db.relationship('Reponse', backref='student', uselist=False)

class Reponse(db.Model):
    __tablename__ = 'reponses'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    formation = db.Column(db.String(200), nullable=False)
    etablissement = db.Column(db.String(200), nullable=False)
    parcours = db.Column(db.Text, nullable=True)
    date_reponse = db.Column(db.DateTime, default=datetime.utcnow)
