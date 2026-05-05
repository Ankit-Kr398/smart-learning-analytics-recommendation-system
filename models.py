from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logs = db.relationship('StudyLog', backref='user', lazy=True)
    reports = db.relationship('WeeklyReport', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    weight = db.Column(db.Float, default=1.0)

    topics = db.relationship('Topic', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'


class Topic(db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    logs = db.relationship('StudyLog', backref='topic', lazy=True)

    def __repr__(self):
        return f'<Topic {self.name}>'


class StudyLog(db.Model):
    __tablename__ = 'study_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    questions_attempted = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False, default='Medium')
    study_time_minutes = db.Column(db.Integer, nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def accuracy(self):
        if self.questions_attempted == 0:
            return 0.0
        return round((self.correct_answers / self.questions_attempted) * 100, 2)

    def __repr__(self):
        return f'<StudyLog user={self.user_id} topic={self.topic_id} date={self.session_date}>'


class WeeklyReport(db.Model):
    __tablename__ = 'weekly_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    week_end = db.Column(db.Date, nullable=False)
    total_sessions = db.Column(db.Integer, default=0)
    total_time_minutes = db.Column(db.Integer, default=0)
    avg_accuracy = db.Column(db.Float, default=0.0)
    productivity_score = db.Column(db.Float, default=0.0)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WeeklyReport user={self.user_id} week={self.week_start}>'