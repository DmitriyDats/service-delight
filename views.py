import os
import os.path as op
from flask import url_for, redirect, request, abort, render_template
from flask_admin.contrib import sqla
from flask_security import current_user, url_for_security
import flask_admin as admin
from flask_admin import form
from jinja2 import Markup
from sqlalchemy.event import listens_for
from models import File, Image

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'static/images/menu-product')
try:
    os.mkdir(file_path)
except OSError:
    pass

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
                return redirect(url_for('admin.login_view', next=request.url))




class SuperUserView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('vipuser'):
            return True

        return False


# Create customized model view class
class MyModelView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('adminrole'):
            return True

        return False

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
                return redirect(url_for('admin.login_view', next=request.url))


# Administrative views
class FileView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

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
                return redirect(url_for('admin.login_view', next=request.url))

    # Override form field to use Flask-Admin FileUploadField
    form_overrides = {
        'path': admin.form.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'Files',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }


class ImageView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

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
                return redirect(url_for('admin.login_view', next=request.url))

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % admin.form.thumbgen_filename(model.path))

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': admin.form.ImageUploadField('Image',
                                            base_path=file_path,
                                            thumbnail_size=(100, 100, True))
    }


# Delete hooks for models, delete files if models are getting deleted
@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass


@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path,
                              admin.form.thumbgen_filename(target.path)))
        except OSError:
            pass


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
        if not current_user.has_role('export'):
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
            self.can_delete = True
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
            self.can_export = True
            return True
        return False