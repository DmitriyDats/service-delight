from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from flask_principal import Principal
from flask_login import LoginManager


# Create application
app = Flask(__name__)

app.config.from_pyfile('config.cfg')
'''
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
'''


db = SQLAlchemy(app)

principals = Principal(app)
login_manager = LoginManager(app)

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(RoleMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    active = db.Column(db.Boolean())
    registered_on = db.Column('registered_on', db.DateTime)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    head_id = db.Column(db.Integer, db.ForeignKey('head.id'))
    heads = db.relationship(
        'Head', backref=db.backref('user', lazy='dynamic')
    )

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.login

    def __repr__(self):
        return '<User %r>' % self.login

    def __str__(self):
        return self.email


# Create models
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    price = db.Column(db.String(64))

    def __str__(self):
        return self.name


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    price = db.Column(db.String(64))

    def __str__(self):
        return self.name


class Title(db.Model):
    __tablename__ = 'titles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    prices = db.relationship('Price', backref='titles', lazy='dynamic')
    #dish_s = db.relationship('Dish', backref='titles', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<name: %s>' % (self.name)


class Dish(db.Model):
    __tablename__ = 'dishes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    #title_id = db.Column(db.Integer, db.ForeignKey('titles.id'))
    #price_s = db.relationship('Price', backref='dishes', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<name: %s>' % (self.name)


class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(128))  # Unicode
    price_name = db.Column(db.String(255))
    the_weight = db.Column(db.String(100))
    titl_id = db.Column(db.Integer, db.ForeignKey('titles.id'))
    #dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'))

    def __init__(self, path, price_name, the_weight):
        self.path = path
        self.price_name = price_name
        self.the_weight = the_weight

    def __repr__(self):
        return '<price_name: %s, the_weight: %s>' % (self.price_name, self.the_weight)


class Head(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    titl_s = db.relationship('Titl', backref='head', lazy='dynamic')


    def __repr__(self):
        return '%s' % (self.name)

class Titl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    City = db.Column(db.String(40), unique=True)
    head_id = db.Column(db.Integer, db.ForeignKey('head.id'))
    pric_s = db.relationship('Pric', backref='titl', lazy='dynamic')

    def __repr__(self):
        return '%s' % (self.City)

class Pric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(40), nullable=False)
    LastName = db.Column(db.String(20), nullable=False)
    titl_id = db.Column(db.Integer, db.ForeignKey('titl.id'))

    def __repr__(self):
        return '%s' % (self.titl_id)
