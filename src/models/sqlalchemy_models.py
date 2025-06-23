from sqlalchemy import Column, String, Float, Integer, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Apartment_DB(Base):
    __tablename__ = "apartment"

    url = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    m2 = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    price = Column(Float)
    embedding = Column(ARRAY(Float))
