from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Channel(db.Model):
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key = True)
    topic = db.Column(db.String, nullable = False)
    creator = db.Column(db.String, nullable = False)
    timedate = db.Column(db.String, nullable = False)
    lastactive = db.Column(db.String, nullable = True)

class Comment(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key = True)
    comment = db.Column(db.String, nullable = False)
    poster = db.Column(db.String, nullable = False)
    timedate = db.Column(db.String, nullable = False)
    channel = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable = False)
