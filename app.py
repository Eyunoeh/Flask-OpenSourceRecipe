from flask import Flask, render_template, request, redirect, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://root:password@localhost/db_food_forum'

db = SQLAlchemy(app)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(200), nullable=False)
    food_recipe = db.Column(db.String(1000), nullable=False)
    food_pic = db.Column(db.LargeBinary(length=(2 ** 32) - 1), nullable=False)
    filename = db.Column(db.String(1000), nullable=False)
    mimetype = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<Food %r>' % self.id


def create_tables():
    with app.app_context():
        db.create_all()


create_tables()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/share-recipe', methods=['POST'])
def share_recipe():
    if request.method == "POST":
        food_name = request.form.get('food_name')
        food_recipe = request.form.get('food_recipe')
        food_pic = request.files.get('food_pic')
        if food_pic:
            filename = secure_filename(food_pic.filename)
            mimetype = food_pic.mimetype
            food_model = Food(food_name=food_name, food_recipe=food_recipe, food_pic=food_pic.read()
                              , filename=filename, mimetype=mimetype)
            db.session.add(food_model)
            db.session.commit()
            return redirect('/')
    else:
        return render_template('index.html')


@app.route('/api/food', methods=["GET", ])
def food():
    if request.method == "GET":
        try:
            foods = Food.query.all()
            food_data = []
            for food_obj in foods:
                food_data.append({
                    "food_name": food_obj.food_name,
                    "food_recipe": food_obj.food_recipe,
                    "food_pic": f"http://127.0.0.1:5000/api/food/images/{food_obj.id}",
                    "filename": food_obj.filename,
                    "mimetype": food_obj.mimetype

                })
            return jsonify(food_data)
        except AttributeError:
            return "error"


@app.route('/api/food/images/<int:id>')
def food_img(id):
    img = Food.query.filter_by(id=id).first()
    if not img:
        return "no image found", 400
    return Response(img.food_pic, mimetype=img.mimetype)


if __name__ == '__main__':
    app.run(debug=True)
