from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import json
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['SECRET_KEY'] = 'e95dcc09e11a8fc70e384b12da8f4a9ea7530645e935343f78dc3b7ad488794a'

db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vk_id = db.Column(db.String(255), unique=True, nullable=False)
    vk_access_token = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"vk_id:{self.vk_id}, name:{self.name}"


@app.route("/")
def auth_page():
    if session.get('user_id'):
        return render_template('profile.html')

    return render_template("auth.html")


@app.route("/")
def profile_page():
    return render_template("profile.html")


@app.route("/receive_text", methods=("POST", "GET"))
def receive_text():

    if request.method == 'POST':
        text = request.form['InputText']
        user = Users.query.filter_by(id=session['user_id']).first()
        from question_handler import question_handler
        question_handler(text, user)
    return redirect(url_for('profile_page'))


@app.route("/logout")
def logout():
    if not session.get('user_id'):
        return redirect(url_for('auth_page'))

    session.pop('user_id', None)
    return redirect(url_for('auth_page'))


@app.route("/vk_callback")
def vk_callback():

    user_code = request.args.get('code')
    if not user_code:
        return redirect(url_for("auth_page"))

    response = requests.get(
        'https://oauth.vk.com/access_token?client_id=7811260&client_secret=74vsDciNiH8XmTiIUFdM&redirect_uri=http://127.0.0.1:5000/vk_callback&code=' + user_code)
    access_token_json = json.loads(response.text)

    if "error" in access_token_json:
        return redirect(url_for("auth_page"))

    vk_id = access_token_json['user_id']
    access_token = access_token_json['access_token']

    response = requests.get(
        f'https://api.vk.com/method/users.get?user_ids={vk_id}&fields=bdate&access_token={access_token}&v=5.130')
    vk_user = json.loads(response.text)

    user = Users.query.filter_by(vk_id=vk_id).first()

    if user is None:
        try:
            name = vk_user['response'][0]['first_name'] + " " + vk_user['response'][0]['last_name']
            new_user = Users(name=name, vk_id=vk_id, vk_access_token=access_token)
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError as err:
            db.session.rollback()
            print(f"Ошибка при добавлении пользователя в БД:{err.__dict__['orig']}")
            return redirect(url_for('auth_page'))
        user = Users.query.filter_by(vk_id=vk_id).first()

    session['user_id'] = user.id
    return redirect(url_for('profile_page'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
