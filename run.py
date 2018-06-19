"""
The file that runs the application
"""
from flask_jwt_extended import JWTManager

from app import app, db
from app.models import RevokedToken
from app.helpers import endpoints


jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)


if __name__ == '__main__':
    app.run()
