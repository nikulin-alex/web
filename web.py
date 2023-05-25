from flask import Flask,render_template,url_for,redirect
import json
import requests
from random import randint
import datetime
#from news import newslist
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,EmailField,SelectField
from wtforms.validators import DataRequired,Optional
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)
coun = 0
app.config['SECRET_KEY'] = 'SECRET_KEY'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    news = db.relationship('News', back_populates='category')

    def __repr__(self):
        return f'Category {self.id}: ({self.title})'
class News(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255),unique=True,nullable=False)
    text = db.Column(db.Text,nullable=False)
    create_date = db.Column(db.DateTime,default=datetime.datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', back_populates='news')

    def __repr__(self):
        return f'News {self.id}: ({self.title.split()[:9]}...)'

app_context = app.app_context()
app_context.push()


def get_categories():
    categories = Category.query.all()
    return [(category.id, category.title) for category in categories]


class NewsForm(FlaskForm):
    name = StringField('введите заголовок новости',validators=[DataRequired()])
    text = StringField('введите текст новости',validators=[DataRequired()])
    category = SelectField('Категория', choices=get_categories())
    subm = SubmitField()


class CategoryForm(FlaskForm):
    name = StringField('введите заголовок категории',validators=[DataRequired()])
    subm = SubmitField()
@app.route('/')
def home():
    newslist = News.query.all()
    categories = Category.query.all()
    return render_template('index.html',newslist=newslist,categories=categories)
@app.route('/about')
def about():
    return f'КОНТАКТЫ!!!!!!!!'
@app.route('/fibonacci')
def fib():
    f1,f2 = 1,1
    fib = [f1,f2]
    for _ in range(100):
        f1,f2 = f2,f1+f2
        fib.append(f2)
    fib1='1'
    for i in range(1,len(fib)):
        fib1+=f',{str(fib[i])}'
    return fib1
@app.route('/money')
def value():
    js = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    js = js['Valute']
    for v in js.items():
        v2 = v['Value']
        v1 = v['Name']
        yield f'1 {v1} - {v2} руб. <br>'
@app.route('/random')
def random():
    with open('C:/Users/Alexander/Desktop/alotofwisdom/code/uchi ru/web/data.txt',mode='r',encoding='UTF-8') as file:
        data = [i.strip('\n') for i in file]
        return data[randint(0,len(data)-1)]
@app.route('/news')
def news():
    return f'На площади Тяньаньмэнь сегодня, как и всегда, ничего не произошло'
@app.route('/news/<int:id>')
def news_home(id):
    new = News.query.get(id)
    categories = Category.query.all()
    return render_template('news_detail.html',new=new,categories=categories)
@app.route('/total/<a>/<b>')
def total(a,b):
    return f'{int(a)+int(b)}'  
def primes(n):
    coun = 0
    d = 2
    p = 2
    while coun < n:
        while d**2 <= p and p % d != 0:
            d += 1
        if d**2>p:
            coun += 1
            yield str(p)+' '
        p += 1
        d = 2
@app.route('/dt/<string:dat>')
def dt(dat):
    now = datetime.datetime.now()
    if dat == 'date':
        return now.strftime('%d.%m.%Y')
    elif dat == 'time':
        return now.strftime('%H.%M.%S.%f')
@app.route('/calc/<int:a>/<string:oper>/<int:b>')
def calc(a,oper,b):
    result = f'{a} {oper} {b}'
    return f'{eval(result)}'
@app.route('/cat')
def cat():
    url_cat = 'https://api.thecatapi.com/v1/images/search'
    response = requests.get(url_cat).json()
    response = response[0]['url']
    return render_template('catdog.html',animal=response)
@app.route('/dog')
def dog():
    url_dog = 'https://api.thedogapi.com/v1/images/search'
    response = requests.get(url_dog).json()
    response = response[0]['url']
    return render_template('catdog.html',animal=response)
@app.route('/add_new',methods=['GET', 'POST'])
def add_new():
    form = NewsForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        news = News()
        news.text = form.text.data
        news.title = form.name.data
        news.create_date = datetime.datetime.now()
        news.category_id = form.category.data
        db.session.add(news)
        db.session.commit()
        return redirect('/')
    return render_template('addnew.html',form=form,categories=categories)
app.add_url_rule('/primes/<int:n>','primes',primes)            
@app.route('/test/<id>')
def test(id):
    return render_template('test.html',id=int(id))


@app.route('/add_category',methods =['GET', 'POST'] )
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = Category()
        cat.title = form.name.data
        db.session.add(cat)
        db.session.commit()
        return redirect('/')
    return render_template('addcat.html',form=form)

@app.route('/category/<int:id>')
def news_in_category(id):
    categories = Category.query.all()
    category = Category.query.get(id)
    news = category.news
    return render_template('category.html',news=news,category=category,categories=categories)




if __name__ == '__main__':
    app.run(debug=True)