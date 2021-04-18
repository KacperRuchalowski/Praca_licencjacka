import os
import secrets
import random

from PIL import Image
from flask import Flask, render_template, redirect, url_for, flash
from flask import request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_ckeditor import CKEditor

from forms import PostForm, LoginForm, QuizForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost:5432/yokai"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ckeditor = CKEditor(app)
login_manager = LoginManager(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = '09412da809127wdawwar'


class Category(db.Model):
    __tablename__ = 'category'

    def __init__(self, name):
        self.name = name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    articles = db.relationship('Article', backref='category')


class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    image = db.Column(db.String())
    image_desc = db.Column(db.String())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    views = db.Column(db.Integer)

    def __init__(self, name, description, image, image_desc):
        self.name = name
        self.description = description
        self.image = image
        self.views = 0
        self.image_desc = image_desc

    def __repr__(self):
        return f"<article {self.name}>"


class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String())
    answer1 = db.Column(db.String())
    answer2 = db.Column(db.String())
    answer3 = db.Column(db.String())
    good_answer = db.Column(db.String())

    def __init__(self, question, answer1, answer2, answer3):
        self.question = question
        self.answer1 = answer1
        self.answer2 = answer2
        self.answer3 = answer3


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=True, nullable=False)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)
    output_size = (300, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def IncrementViews(art_ID):
    article = Article.query.filter(Article.id == art_ID).first()
    article.views += 1
    db.session.commit()


def GetMostPopularArticles():
    popular_articles = Article.query.order_by(Article.views.desc()).limit(5).all()
    results = [
        {
            "Title": article.name,
            "Desc": article.description,
            "ID": article.id,
            "Views": article.views,
            "Image_desc": article.image_desc

        } for article in popular_articles]
    return results


@app.route('/knowledge')
def knowledge():
    return render_template('knowledge.html', popular=GetMostPopularArticles())


@app.route('/quiz', methods=['POST', 'GET'])
def quiz():
    allQuestions = Quiz.query.all()

    results = [
        {
            "Question": question.question,
            "Answers": [question.answer1, question.answer2, question.answer3],
            "GoodAnswer": question.good_answer,
            "ID": question.id

        } for question in allQuestions]

    if request.method == 'POST':
        points = 0
        answers = request.form
        good_answers = []
        bad_answers = []

        for pnr, odp in answers.items():
            if odp == results[int(pnr)]['GoodAnswer']:
                points += 1
                good_answers.append(odp)
            else:
                bad_answers.append(odp)

        return render_template('quiz_results.html', popular=GetMostPopularArticles(), quiz=results, points=points
                               , answer=good_answers, bad_answers=bad_answers)

    return render_template('quiz.html', popular=GetMostPopularArticles(), quiz=results)


@app.route('/newPost', methods=['POST', 'GET'])
def newPost():
    available_posts = db.session.query(Category).all()
    post_list = [(i.id, i.name) for i in available_posts]
    form = PostForm()
    form.category.choices = post_list

    if form.validate_on_submit():
        picture_file = save_picture(form.image.data)
        article = Article(name=form.title.data, description=form.content.data, image=picture_file,
                          image_desc=form.image_description.data)
        article.category_id = form.category.data
        db.session.add(article)
        db.session.commit()
        flash('Dodano nowy artykuł!', 'success')
        return redirect(url_for('handle_articles'))

    return render_template('newPost.html', title='Nowy artykuł', form=form, legend='Nowy artykuł')


@app.route('/newQuiz', methods=['POST', 'GET'])
def newQuiz():
    form = QuizForm()

    if form.validate_on_submit():
        question = Quiz(question=form.question.data, answer1=form.answer1.data, answer2=form.answer2.data,
                        answer3=form.answer3.data)
        if form.good_answer.data == 'Odpowiedź 1':
            question.good_answer = form.answer1.data
        elif form.good_answer.data == 'Odpowiedź 2':
            question.good_answer = form.answer2.data
        elif form.good_answer.data == 'Odpowiedź 3':
            question.good_answer = form.answer3.data
        db.session.add(question)
        db.session.commit()
        flash('Dodano nowe pytanie!', 'success')
        return redirect(url_for('handle_articles'))

    return render_template('newQuiz.html', title='Nowy artykuł', form=form, legend='Nowy artykuł')


@app.route('/updatePost/<int:postID>', methods=['POST', 'GET'])
def updatePost(postID):
    post = Article.query.get_or_404(postID)

    available_posts = db.session.query(Category).all()
    # Now forming the list of tuples for SelectField
    post_list = [(i.id, i.name) for i in available_posts]

    form = PostForm()
    form.category.choices = post_list

    if form.validate_on_submit():
        post.name = form.title.data
        post.description = form.content.data
        post.category_id = form.category.data
        post.image_desc = form.image_description.data
        picture_file = save_picture(form.image.data)
        post.image = picture_file
        flash('Zaktualizowano', 'success')
        db.session.commit()
        return redirect(url_for('handle_articles'))

    elif request.method == 'GET':
        form.title.data = post.name
        form.content.data = post.description

    return render_template('newPost.html', title='Aktualizuj artykuł', form=form, legend='Aktualizuj artykuł')


@app.route('/deletePost/<int:postID>', methods=['POST', 'GET'])
def deletePost(postID):
    post = Article.query.get_or_404(postID)
    db.session.delete(post)
    db.session.commit()
    flash('Usnięto artykuł', 'success')
    return redirect(url_for('handle_articles'))


@app.route('/deleteQuestion/<int:questionID>', methods=['POST', 'GET'])
def deleteQuestion(questionID):
    question = Quiz.query.get_or_404(questionID)
    db.session.delete(question)
    db.session.commit()
    flash('Usnięto pytanie', 'success')
    return redirect(url_for('handle_articles'))


@app.route('/articles', methods=['POST', 'GET'])
def handle_articles():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_article = Article(name=data['name'], description=data['description'], image=data['image'],
                                  image_desc=data['image'])
            db.session.add(new_article)
            db.session.commit()
            return {"message": f"car {new_article.name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        articles = Article.query.all()
        results = [
            {
                "Title": article.name,
                "Desc": article.description,
                "ID": article.id,
                "image": article.image,
                "Image_desc": article.image_desc

            } for article in articles]

        categories = Category.query.all()
        resultsCategory = [
            {
                "Title": category.name,
                "ID": category.id

            } for category in categories]

        return render_template('articles.html', articles=results, categories=resultsCategory,
                               popular=GetMostPopularArticles(), title="Strona główna")


@app.route('/randomArticle')
def random_article():
    allArticles = Article.query.all()

    idList = []

    for ids in allArticles:
        idList.append(ids.id)

    randArt = random.choice(idList)

    articles = Article.query.filter(Article.id == randArt)

    results = [
        {
            "Title": article.name,
            "Desc": article.description,
            "Image": article.image,
            "Views": article.views,
            "Image_desc": article.image_desc
        } for article in articles]

    categories = Category.query.all()
    categors = [
        {
            "Title": category.name,
            "ID": category.id,
        } for category in categories]

    IncrementViews(randArt)

    return render_template('single_article.html', article=results, popular=GetMostPopularArticles(),
                           categories=categors)


@app.route('/categories', methods=['POST', 'GET'])
def handle_categories():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_category = Category(name=data['name'])
            db.session.add(new_category)
            db.session.commit()
            return {"message": f"car {new_category.name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        categories = Category.query.all()
        results = [
            {
                "Title": category.name,
                "ID": category.id,
            } for category in categories]

        return render_template('base_template.html', result=results)


@app.route('/article/<articleID>')
def single_article(articleID):
    articles = Article.query.filter(Article.id == articleID)

    singleArticle = [
        {
            "Title": article.name,
            "Desc": article.description,
            "Image": article.image,
            "Views": article.views,
            "Image_desc": article.image_desc
        } for article in articles]

    IncrementViews(articleID)

    categories = Category.query.all()
    results = [
        {
            "Title": category.name,
            "ID": category.id,
        } for category in categories]

    popular = GetMostPopularArticles()

    return render_template('single_article.html', article=singleArticle, categories=results, popular=popular)


@app.route('/category/<categoryID>')
def single_category(categoryID):
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter(Article.category_id == categoryID).paginate(page=page, per_page=3)

    categories = Category.query.all()

    current_category = categoryID

    results = [
        {
            "Title": category.name,
            "ID": category.id,
        } for category in categories]

    return render_template('single_category.html', article=articles, categories=results,
                           current_category=current_category,
                           popular=GetMostPopularArticles())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('handle_articles'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password:
            login_user(user, remember=form.remember.data)
            flash('Zalogowano!', 'success')
            return redirect(url_for('handle_articles'))
        else:
            flash('Podano złe dane. Proszę sprawdź czy wpisano poprawne hasło i login', 'danger')
            return redirect(url_for('handle_articles'))
    return render_template('login.html', title='Logowanie', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('handle_articles'))


if __name__ == '__main__':
    app.run()

if __name__ == '__main__':
    app.run(debug=True)
