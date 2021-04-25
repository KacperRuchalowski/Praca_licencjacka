from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FileField, PasswordField, BooleanField, RadioField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    kanji = StringField('Zapis kanji', validators=[DataRequired()])
    kana = StringField('Zapis kana', validators=[DataRequired()])
    content = CKEditorField('Treść', validators=[DataRequired()])
    category = SelectField('Kategoria', coerce=int)
    image_description = StringField('Opis zdjęcia', validators=[DataRequired()])
    image = FileField('Zdjęcie', validators=[FileAllowed(['jpg', 'png'], FileRequired())])
    submit = SubmitField('Akceptuj')


class QuizForm(FlaskForm):
    question = StringField('Pytanie', validators=[DataRequired()])
    answer1 = StringField('Odpowiedź 1', validators=[DataRequired()])
    answer2 = StringField('Odpowiedź 2', validators=[DataRequired()])
    answer3 = StringField('Odpowiedź 3', validators=[DataRequired()])
    good_answer = SelectField('Prawidłowa odpowiedź', choices=['Odpowiedź 1', 'Odpowiedź 2', 'Odpowiedź 3'])
    help_link = SelectField('Nazwa artykułu pomocniczego', coerce=str)
    submit = SubmitField('Akceptuj')


class LoginForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Hasło', validators=[DataRequired(), Length(min=2, max=20)])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj się')


class SearchForm(FlaskForm):
    searchContent = StringField('Wyszukiwarka', validators=[Length(min=2, max=20)])
    submit = SubmitField('Szukaj')
