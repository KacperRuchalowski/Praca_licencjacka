from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FileField, PasswordField, BooleanField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    content = CKEditorField('Treść', validators=[DataRequired()])
    category = SelectField('Kategoria', coerce=int)
    image = FileField('Zdjęcie', validators=[FileAllowed(['jpg', 'png'], FileRequired())])
    submit = SubmitField('Akceptuj')


class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=2, max=20)])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')

