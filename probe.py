import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers

# Create Flask application
app = Flask(__name__)

app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define models directly without reflection...
class Customer(db.Model):
    CustomerId = db.Column(db.Integer(), primary_key=True)
    FirstName = db.Column(db.Unicode(40), nullable=False)
    LastName = db.Column(db.String(20), nullable=False)
    City = db.Column(db.Unicode(40))
    Email = db.Column(db.Unicode(60), unique=True)

    def __str__(self):
        return self.CustomerID

class City(db.Model):
    Id = db.Column(db.Integer(), primary_key=True)
    City = db.Column(db.Unicode(40), unique=True)

    def __str__(self):
        return self.ID

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Flask views
@app.route('/')
def index():
    return render_template('index.html')


# Create customized model view class
class dgBaseView(sqla.ModelView):

    column_display_pk = True
    page_size = 20
    can_view_details = True
    #can_export = False
    can_export = True

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class regularRbacView(dgBaseView):

    def is_accessible(self):

        # set accessibility...
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        # roles not tied to ascending permissions...
        if  not current_user.has_role('export'):
            self.can_export = False

        # roles with ascending permissions...
        if current_user.has_role('adminrole'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True
        if current_user.has_role('supervisor'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = False
            return True
        if current_user.has_role('user'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = False
            return True
        if current_user.has_role('create'):
            self.can_create = True
            self.can_edit = False
            self.can_delete = False
            return True
        if current_user.has_role('read'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        return False

class lookupRbacView(dgBaseView):

    def is_accessible(self):
        # set accessibility...
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        # roles not tied to ascending permissions...
        if  not current_user.has_role('export'):
            self.can_export = False

        # roles with ascending permissions...
        if current_user.has_role('adminrole'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            self.can_export = True
            return True
        if current_user.has_role('supervisor'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = False
            return True
        if current_user.has_role('user'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        if current_user.has_role('create'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        if current_user.has_role('read'):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            return True
        return False

class SuperView(dgBaseView):

    can_export = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('adminrole'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            #self.can_export = True
            return True
        return False


# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )

# Create admin
admin = flask_admin.Admin(
    app, 'Rbac RoleBasedAccess', base_template='my_master.html', template_mode='bootstrap3',
)

class customer_view(regularRbacView):

    column_searchable_list = ['CustomerId', 'City',  'Email', 'FirstName', 'LastName',]
    # make sure the type of your filter matches your hybrid_property
    column_filters = ['FirstName', 'LastName',  'City',  'Email'   ]
    # column_default_sort = ('part_timestamp', True)
    #column_export_list = ['CustomerId', 'City',  'Email', 'FirstName', 'LastName',]



# Add model views
admin.add_view(SuperView(Role, db.session))
admin.add_view(SuperView(User, db.session))
admin.add_view(customer_view(Customer, db.session))
admin.add_view(lookupRbacView(City, db.session))


def build_sample_db():
    """
    Populate a small db with some example entries.
    """
    import string

    #db.drop_all()
    db.create_all()

    with app.app_context():
        read_role = Role(name='read')
        user_role = Role(name='user')
        super_user_role = Role(name='adminrole')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.add(Role(name='read'))
        db.session.add(Role(name='create'))
        db.session.add(Role(name='supervisor'))
        db.session.add(Role(name='delete'))
        db.session.add(Role(name='export'))
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )


        first_names = [
            'read', 'create', 'user', 'suser',  'delete',   'Charlie', 'Sophie',  'Mia',
        ]
        last_names = [
            'Brown', 'Smith',  'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
        ]
        roles1 = [
            'read',  'create',  'user', 'supervisor', 'delete', 'read', 'read', 'read',
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower()
            # initialize the users with simple password...  'a'
            tmp_pass = 'a'
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=encrypt_password(tmp_pass),
                roles=[read_role, ]
            )
        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()
    app.run(host='0.0.0.0', port=5000, debug=True)