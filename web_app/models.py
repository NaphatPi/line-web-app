from flask_login import UserMixin
from web_app import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.String(50), unique=True, primary_key=True)
    name = db.Column(db.String(30), nullable=True)
    surname = db.Column(db.String(30))
    status = db.Column(db.String(10))
    displayName = db.Column(db.String(50))
    dealer = db.Column(db.String(50))
    position = db.Column(db.String(30))
    pictureUrl = db.Column(db.String(300), nullable=True)
    log = db.Column(db.String())

    def __repr__(self):
        return f'''
name   : {self.name}
surname: {self.surname}
status : {self.status}
dpName : {self.displayName}
dealer : {self.dealer}
positn : {self.position}
userId : {self.userId}
picUrl : {self.pictureUrl}
'''

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    role = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Admin: {self.username}  Role: {self.role}'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100), nullable=True)
    hex = db.Column(db.String(30), nullable=False)
    link=db.Column(db.String(100), nullable=False)
    uploadBy = db.Column(db.String(30), nullable=False)
    uploadDate = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tag = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'Document: {self.id}  Title: {self.title}'