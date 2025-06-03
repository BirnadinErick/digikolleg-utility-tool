from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///posts.db")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class PostRecord(Base):
    __tablename__ = "linkedin_posts"
    id = Column(Integer, primary_key=True)
    event_title = Column(String(255))
    date = Column(String(50))
    description = Column(Text)
    good = Column(Text)
    bad = Column(Text)
    goal = Column(Text)
    post = Column(Text)
    instructions = Column(Text)
    status = Column(String(50), default="queued")  # queued / processing / done / failed
