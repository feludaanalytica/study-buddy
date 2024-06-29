from fastapi import FastAPI
from sqladmin import Admin, ModelView
from study_buddy.utilities.dbengine import db_engine
from study_buddy.dashboard.schemas.models.user import User


app = FastAPI()
admin = Admin(app, db_engine)


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.first_name,
        User.last_name,
        User.email,
        User.password
    ]


# Base.metadata.create_all(db_engine)  # Create tables
admin.add_view(UserAdmin)