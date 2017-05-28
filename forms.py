from wtforms import Form, validators, fields, StringField
from werkzeug.security import check_password_hash
from models import User, db


# Define login and registration forms (for flask-login)
class LoginForm(Form):
    user_message = 'Mailing address should be no more than 60 characters'
    user_required = 'Please enter your login.'
    pass_message = 'Password should be no more than 50 characters'
    pass_required = 'Please enter your password.'

    login = fields.StringField('Username', validators=[validators.Length(message=user_message, max=60),
                                                       validators.required(user_required)])
    password = fields.PasswordField('Password', validators=[validators.Length(message=pass_message, max=50),
                                                            validators.required(pass_required)])

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')


class RegistrationForm(Form):
    username_message = 'The name must be at least 4 letters and no more than 25 characters'
    username_required = 'Please enter your login.'
    email_address_message = 'Mailing address should be no more than 60 characters'
    email_address_required = 'Please enter your email address.'
    password_message = 'Passwords must match'

    login = fields.StringField('Username', validators=[validators.Length(message=username_message, min=4, max=25),
                                                       validators.required(username_required)])
    email = fields.StringField('Email', validators=[validators.Length(message=email_address_message, max=60),
                                                    validators.required(email_address_required)])
    password = fields.PasswordField('Password', validators=[validators.required(password_message),
                                                            validators.EqualTo('confirm',
                                                                               message='Passwords must match')])
    confirm = fields.PasswordField('Repeat Password')

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')
        if db.session.query(User).filter_by(email=self.email.data).count() > 0:
            raise validators.ValidationError('Duplicate email')

'''
class ListTitle(Form):
    title_required = 'Please enter your name Title.'
    title_message = 'The name Title must be at least 4 letters and no more than 40 characters'

    name = fields.StringField('Title Cafe', validators=[validators.required(title_required),
                                                        validators.Length(message=title_message, min=4, max=40)])


class ListPrice(Form):
    name_required = 'Please enter your name product.'
    price_required = 'Please enter your price product.'
    img_required = 'Please enter your img.'
    weight_required = 'Please enter your weight'
    name_message = 'The name product must be at least 4 letters and no more than 45 characters'
    price_message = 'The price must be at least 4 letters and no more than 20 characters'
    the_weight_message = 'The price must be at least 4 letters and no more than 20 characters'

    path = fields.StringField('Images', validators=[validators.required(img_required)])
    price_name = fields.StringField('Prices name', validators=[validators.required(price_required),
                                                          validators.Length(message=price_message, min=4, max=20)])
    the_weight = fields.StringField('The_weight', validators=[validators.required(weight_required),
                                                              validators.Length(message=the_weight_message, min=4,
                                                                                max=20)])

class ListDish(Form):
    dish_required = 'Please enter your name Dish.'
    dish_message = 'The name Dish must be at least 4 letters and no more than 25 characters'

    name = fields.StringField('Title Dish', validators=[validators.required(dish_required),
                                                        validators.Length(message=dish_message, min=4, max=25)])
'''


