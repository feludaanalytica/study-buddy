from sqlalchemy import create_engine
from study_buddy.utilities.constants import DATABASE_URL


db_engine = create_engine(DATABASE_URL)
