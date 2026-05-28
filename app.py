#skeleton flask


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash


from models import User
from extensions import db

app = Flask(__name__)

from routes.auth import auth
from routes.admin import admin
from routes.company import company
from routes.student import student

app.config['SECRET_KEY'] = 'change-this-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placementapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(company, url_prefix='/company')
app.register_blueprint(student, url_prefix='/student')


from models import *


# @app.route('/test')
# def test():
#     return render_template('index.html')

#mian stufff
@app.route('/')
def home():
    return render_template('auth/index.html')
    #return "<h1>Welcome to Placement Portal!</h1>"


# #iffy
# @app.route('/resume')
# def resume():
#     return "<h1>Resume Display Page</h1><h5>can be accessed by admin (via application page) and student</h5>"


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    #make admin user after!!!!!
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                #user_id = 1000,
                username='admin',
                email='24f3001002@ds.study.iitm.ac.in',
                password_hash=generate_password_hash('password1526'),
                role='admin'
                )
            db.session.add(admin)
            db.session.commit()

    print(app.url_map)
    app.run(debug=True)
