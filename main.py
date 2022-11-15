from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import sqlalchemy.orm.query

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///films-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


db.drop_all()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String())
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String())
    img_url = db.Column(db.String())

    def __repr__(self):
        return f"<Movie {self.title}>"


db.create_all()


class EditForm(FlaskForm):
    rating = StringField(label="New Rating:", validators=[DataRequired()])
    review = StringField(label="New Review:", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


class AddForm(FlaskForm):
    title = StringField(label="Title:")
    submit = SubmitField(label="Submit")


API_KEY = "b51a884e57fb184f12b4d3f3ae4defb4"
API_URL = "https://api.themoviedb.org/3/search/movie?"


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/update", methods=["GET", "POST"])
def update():
    form = EditForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()

    if form.validate_on_submit():
        parameters = {
            "api_key": "b51a884e57fb184f12b4d3f3ae4defb4",
            "query": form.title.data,
        }
        movie_database = requests.get(API_URL, params=parameters)
        movie_json = movie_database.json()["results"]
        return render_template("select.html", movies=movie_json)

    return render_template("add.html", form=form)


@app.route("/selector")
def selector():
    movie_api_id = request.args.get('id')
    api_url = f"https://api.themoviedb.org/3/movie/{movie_api_id}?"
    parameters = {
        "movie_id": movie_api_id,
        "api_key": "b51a884e57fb184f12b4d3f3ae4defb4"
    }
    if movie_api_id:
        movie_api = requests.get(api_url, params=parameters)
        data = movie_api.json()
        new_object = Movie(
            title=data['original_title'],
            year=data['release_date'][0:4],
            description=data['overview'],
            img_url="https://image.tmdb.org/t/p/w500" + data['poster_path']
        )
        db.session.add(new_object)
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5007)
