from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    token = db.Column(db.String(128))
    avatar = db.Column(db.String(128))
    Comments = db.relationship('Comment', backref='user')
    subComments = db.relationship('subComment', backref='user')



    def makePassword(self, password):
        return generate_password_hash(password)


    def checkPassword(self, password):
        return check_password_hash(self.password, password)



class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)
    subComments = db.relationship('subComment', backref='comment')
    uploadTime = db.Column(db.DateTime, default=datetime.now())



class subComment(db.Model):
    __tablename__ = 'subcomment'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    parentCommentId = db.Column(db.Integer, db.ForeignKey('comment.id'))
    text = db.Column(db.Text)
    uploadTime = db.Column(db.DateTime, default=datetime.now())



class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


    def makePassword(self, password):
        return generate_password_hash(password)


    def checkPassword(self, password):
        return check_password_hash(self.password, password)