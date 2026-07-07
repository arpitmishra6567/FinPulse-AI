from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import DATABASE_URL
from backend.app.database.models import Base
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
def init_db(): Base.metadata.create_all(engine)