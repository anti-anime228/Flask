
# from flask_login import UserMixin, login_user, current_user, logout_user, login_required
# from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
