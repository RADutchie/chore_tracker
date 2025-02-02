# project/server/models.py


import datetime

from flask import current_app
from flask_login import UserMixin

from project.server import bcrypt, db


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user_name, password, admin=False):
        self.user_name = user_name
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode("utf-8")
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password, current_app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode("utf-8")

    def __repr__(self):
        return "<User {0}>".format(self.user_name)


class Child(db.Model):

    __tablename__ = "children"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Child {0}>".format(self.name)


class Chore(db.Model):

    __tablename__ = "chores"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chore = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __init__(self, chore, value):
        self.chore = chore
        self.value = value

    def __repr__(self):
        return "<Chore {0}>".format(self.chore)


class CompletedChore(db.Model):

    __tablename__ = "completed_chores"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chore_id = db.Column(db.Integer, db.ForeignKey('chores.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    completed_on = db.Column(db.Date, nullable=False, default=datetime.datetime.now())
    value = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    chore = db.relationship('Chore', backref='completed_instances')
    child = db.relationship('Child', backref='completed_instances')
    user = db.relationship('User', backref='completed_instances')

    def __init__(self, chore_id, child_id, user_id, completed_on=None):
        self.chore_id = chore_id
        self.child_id = child_id
        self.user_id = user_id
        self.completed_on = completed_on if completed_on else datetime.datetime.now()
        self.value = Chore.query.get(chore_id).value

    def __repr__(self):
        return "<CompletedChore {0}>".format(self.id)


class WeeklyTotals(db.Model):

    __tablename__ = "weekly_totals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)
    total = db.Column(db.Float, nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_on = db.Column(db.Date)

    child = db.relationship('Child', backref='weekly_totals')
    approver = db.relationship('User', backref='validated_totals')

    def __init__(self, child_id, week_start, total=None, approved_by=None, approved_on=None):
        self.child_id = child_id
        self.week_start = week_start
        self.total = total
        self.approved_by = approved_by
        self.approved_on = approved_on

    def __repr__(self):
        return "<WeeklyTotals {0}>".format(self.id)
