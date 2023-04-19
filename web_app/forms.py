from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, PasswordField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError
from web_app.models import Document

class RegisterForm(FlaskForm):
    name = StringField(label="ชื่อ", validators=[DataRequired(message='กรุณาระบุชื่อ'), Length(min=1, max=30)])

    surname = StringField(label="นามสกุล", validators=[DataRequired(message='กรุณาระบุนามสกุล'), Length(min=1,max=30)])

    dealer = SelectField(label="ศูนย์บริการ", choices=['choose your organization', 'organization 1', 'organization 2', 'organization 3', 'organization 4'], validators=[DataRequired(message='Please specify your organization')])

    position = SelectField(label="ตำแหน่งงาน", choices=['Choose your position', 'position 1', 'position 2', 'position 3', 'position 4'])

    submit = SubmitField('ลงทะเบียน')


class UserLoginForm(FlaskForm):
    userIDToken = StringField(label="userIDToken", validators=[Length(max=1000)])
    getOS = StringField(label="getOS", validators=[Length(max=10)])
    isInClient = StringField(label="isInClient", validators=[Length(max=10)])
    getFriendShip = StringField(label="getFriendShip", validators=[Length(max=10)])
    btnSubmit = SubmitField('')


class AdminLoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(max=30)])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(max=30)])
    remember_me = BooleanField('Keep me logged in')
    btnSubmit = SubmitField('Login')

class NewDocumentForm(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired(), Length(max=100)])
    description = StringField(label="Description", validators=[Length(max=100)])
    tag = StringField(label="Tag", validators=[Length(max=12)])
    docFile = FileField('Upload pdf file', validators=[DataRequired(), FileAllowed(['pdf'])])
    btnSubmit = SubmitField('Create')

    def validate_title(self, title):
        title = Document.query.filter_by(title=title.data).first()
        if title:
            raise ValidationError('Title already exists. Please choose another title.')