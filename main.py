import os
from flask import Flask
from flask_security import Security, hash_password, SQLAlchemySessionUserDatastore
from application.database import db
from application.models import *
from flask_restful import Api
from application.config import LocalDevelopmentConfig

app, api = None, None
def create_app():
    app = Flask(__name__)
    if os.getenv('ENV', "development")== "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("started local development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    api = Api(app)
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    app.security = Security(app, user_datastore)
    
    app.security.datastore.find_or_create_role(
        name="admin", permissions=["user-read", "user-write", "user-delete", "user-update"]
    )
    db.session.commit()
    if not app.security.datastore.find_user(email="test@me.com"):
        app.security.datastore.create_user(email="test@me.com",
        password=hash_password("password"), roles=["admin"])
    db.session.commit()
    return app, api
app, api = create_app()

from application.manager_views import *
from application.user_views import *

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8000)
