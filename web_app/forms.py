from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField, PasswordField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError
from web_app.models import Document

class RegisterForm(FlaskForm):
    name = StringField(label="ชื่อ", validators=[DataRequired(message='กรุณาระบุชื่อ'), Length(min=1, max=30)])

    surname = StringField(label="นามสกุล", validators=[DataRequired(message='กรุณาระบุนามสกุล'), Length(min=1,max=30)])

    dealer = SelectField(label="ศูนย์บริการ", choices=['เลือกศูนย์บริการ', 'TIS group', 'ศูนย์บริการ 1', 'ศูนย์บริการ 2', 'ศูนย์บริการ 3'], validators=[DataRequired(message='โปรดระบุศูนย์บริการของท่าน')])

    position = SelectField(label="ตำแหน่งงาน", choices=['เลือกตำแหน่งงาน', 'ผู้จัดการศูนย์', 'ครูฝึก', 'หัวหน้าที่ปรึกษางานบริการ (SA)', 'เจ้าหน้าที่เคลม'])

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