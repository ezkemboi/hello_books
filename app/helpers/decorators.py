"""Contains all decorators to help in implementing the app"""
from functools import wraps
from flask_jwt_extended import get_jwt_identity

from app.models import User


def admin_required(func):
    """Allow setting of admin required decorator to be used for all functions"""

    @wraps(func)
    def check_admin(*args, **kwargs):
        """Check if user is an admin"""
        admin_credentials = User.query.filter(User.email.endswith('@hellobookslibrary.com'),
                                              User.user_id == get_jwt_identity()).first()
        if not admin_credentials:
            return {"message": "Only admin can add a book."}, 403
        return func(*args, **kwargs)
    return check_admin
