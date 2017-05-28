import os
from flask import render_template, url_for, redirect, request, flash
from flask_security import Security, SQLAlchemyUserDatastore, current_user
import flask_login as login
from flask_admin import helpers as admin_helpers
from flask_admin import helpers, expose
import flask_admin as admin
from werkzeug.security import generate_password_hash
from flask_principal import RoleNeed, identity_loaded, UserNeed
from models import app, login_manager

from models import db, User, Role, File, Image, Price, Title, Dish, Pric, Titl, Head
from forms import LoginForm, RegistrationForm  # , ListPrice, ListTitle, ListDish
from views import MyModelView, ImageView, FileView, regularRbacView, lookupRbacView


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def index(self):

        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=['GET', 'POST'])
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)

        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated:
            flash('Welcome' + ' ' + current_user.login + ' ' + 'you are logged in to your personal account')
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for(
            '.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=['GET', 'POST'])
    def register_view(self):
        form = RegistrationForm(request.form)

        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for(
            '.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


def common_args():
    name = 'Exit'
    if login.current_user.is_authenticated:
        name = 'Room' + ' ' + current_user.login
    return {'name': name}


# Flask views
@app.route('/')
def index():
    title_head = 'Service Delight'

    return render_template('index.html',
                           title_head=title_head,
                           **common_args())


@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # form = ListPrice(request.form)
    # form1 = ListTitle(request.form)
    # form2 = ListDish(request.form)
    title_head = 'institutions'

    return render_template('project_templates/menu.html',
                           title_head=title_head,
                           # form=form,
                           # form1=form1,
                           # form2=form2,
                           titles=Title.query.all(),
                           dishes=Dish.query.all(),
                           prices=Price.query.all(),
                           **common_args())


@app.route('/institution')
def institution():
    title_head = 'institution'
    return render_template('project_templates/institutions.html',
                           title_head=title_head,
                           headers=Head.query.all(),
                           **common_args())


@app.route('/contacts')
def contacts():
    title_head = 'contacts'
    return render_template('project_templates/contacts.html',
                           title_head=title_head,
                           **common_args())


@app.route('/list_product')
def list_product():
    title_head = 'products'
    return render_template('project_templates/list-product.html',
                           title_head=title_head,
                           titles=Titl.query.all(),
                           prices=Pric.query.all(),
                           **common_args())


@app.route('/delivery')
def delivery():
    title_head = 'delivery'
    return render_template('project_templates/delivery.html',
                           title_head=title_head,
                           **common_args())


@app.route('/company')
def company():
    title_head = 'company'
    return render_template('project_templates/company.html',
                           title_head=title_head,
                           **common_args())


@app.route('/order')
def order():
    title_head = 'order'
    return render_template('project_templates/order.html',
                           title_head=title_head,
                           **common_args())


# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, index_view=MyAdminIndexView(), base_template='my_master.html')


class head_view(regularRbacView):
    column_searchable_list = ['id', 'name']
    # make sure the type of your filter matches your hybrid_property
    column_filters = ['name']
    # column_default_sort = ('part_timestamp', True)
    # column_export_list = ['CustomerId', 'City',  'Email', 'FirstName', 'LastName',]


class customer_view(regularRbacView):
    column_searchable_list = ['id', 'FirstName', 'LastName', 'titl_id']
    # make sure the type of your filter matches your hybrid_property
    column_filters = ['FirstName', 'LastName', 'titl_id']
    # column_default_sort = ('part_timestamp', True)
    # column_export_list = ['CustomerId', 'City',  'Email', 'FirstName', 'LastName',]


class look_view(lookupRbacView):
    column_searchable_list = ['id', 'City']
    # make sure the type of your filter matches your hybrid_property
    column_filters = ['City']
    # column_default_sort = ('part_timestamp', True)
    # column_export_list = ['CustomerId', 'City',  'Email', 'FirstName', 'LastName',]


# Add view
admin.add_view(MyModelView(User, db.session, name='Shoppers'))
admin.add_view(MyModelView(Role, db.session, name='Roles'))
admin.add_view(FileView(File, db.session))
admin.add_view(ImageView(Image, db.session, name='Order'))
admin.add_view(customer_view(Pric, db.session))
admin.add_view(look_view(Titl, db.session))
admin.add_view(head_view(Head, db.session))


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='adminrole')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.add(Role(name='create'))
        db.session.add(Role(name='supervisor'))
        db.session.add(Role(name='delete'))
        db.session.add(Role(name='export'))
        db.session.commit()

        test_user = user_datastore.create_user(
            login='Admin',
            email='admin',
            password=generate_password_hash('admin'),
            roles=[user_role, super_user_role]
        )
        db.session.add(test_user)
        db.session.commit()
    return


if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    # Start app
    app.run(debug=True)

'''
@app.route('/menu/title', methods=['GET', 'POST'])
def title_add():
    form1 = ListTitle(request.form)
    if request.method == 'POST' and form1.validate():
        new_title = Title(request.form['name'])
        db.session.add(new_title)
        db.session.commit()
        return redirect(url_for('menu'))

    return render_template('project_templates/menu.html',
                           form1=form1,
                           titles=Title.query.all())


@app.route('/menu/dish', methods=['GET', 'POST'])
def dish_add():
    form2 = ListDish(request.form)
    if request.method == 'POST' and form2.validate():
        new_dish = Dish(request.form['name'])
        db.session.add(new_dish)
        db.session.commit()

        return redirect(url_for('menu'))

    return render_template('project_templates/menu.html',
                           form2=form2,
                           dishes=Dish.query.all())


@app.route('/menu/add', methods=['GET', 'POST'])
def price_add():
    form = ListPrice(request.form)
    if request.method == 'POST' and form.validate():
        new_price = Price(request.form['path'], request.form['price_name'], request.form['the_weight'])
        db.session.add(new_price)
        db.session.commit()

        return redirect(url_for('menu'))

    return render_template('project_templates/menu.html',
                           form=form,
                           prices=Price.query.all())




@app.route('/menu/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    if request.method == 'GET':
        title = Title.query.get(id)
        db.session.delete(title)
        db.session.commit()

        return redirect(url_for('menu',
                                titles=Title.query.all()))


@app.route('/menu/deletes/<id>', methods=['GET', 'POST'])
def delete_price(id):
    if request.method == 'GET':
        price = Price.query.get(id)
        db.session.delete(price)
        db.session.commit()

        return redirect(url_for('menu',
                                prices=Price.query.all()))


@app.route('/menu/del/<id>', methods=['GET', 'POST'])
def delete_dish(id):
    if request.method == 'GET':
        dish = Dish.query.get(id)
        db.session.delete(dish)
        db.session.commit()

        return redirect(url_for('menu',
                                dishes=Dish.query.all()))




@app.route('/menu/edit/<id>', methods=['GET'])
def edit(id):
    form1 = ListTitle(request.form)
    return render_template('project_templates/edit.html',
                           form1=form1,
                           title=Title.query.get(id),
                           dish=Dish.query.get(id),
                           price=Price.query.get(id))


@app.route('/menu/<id>', methods=['POST'])
def update(id):
    title = Title.query.get(id)
    title.name = request.form['name']
    dish = Dish.query.get(id)
    dish.name = request.form['name']
    db.session.add(title)
    db.session.add(dish)
    db.session.commit()

    return redirect(url_for('menu',
                            title=title))
'''
