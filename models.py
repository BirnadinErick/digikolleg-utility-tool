import datetime

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, desc
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import dotenv_values

config = dotenv_values(".env")

engine = create_engine(config["DATABASE_URI"])
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class OTPRecord(Base):
    __tablename__ = "OTPRecord"
    id = Column(Integer, primary_key=True)
    code = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.now())
    task_id = Column(Integer)  # no need for full relationship for now


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
    status = Column(
        String(50), default="queued"
    )  # queued / approved / processing / done / failed
    posttype = Column(String(50), default="regular") # regular / messe / ILP

    def dict(self):
        return {
            "event_title": self.event_title,
            "date": self.date,
            "description": self.description,
            "good": self.good,
            "bad": self.bad,
            "goal": self.goal,
            "instructions": self.instructions,
        }

    def api_dict(self):
        return {
            "event_title": self.event_title,
            "date": self.date,
            "description": self.description,
            "good": self.good,
            "bad": self.bad,
            "goal": self.goal,
            "instructions": self.instructions,
            "post": self.post,
            "posttype": self.posttype
        }

    def get_post(self):
        return {
            "post": self.post,
            "event_title": self.event_title,
        }


if __name__ == "__main__":
    Base.metadata.create_all(engine)
