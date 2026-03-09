from sqlalchemy import Boolean, Column, Integer, Text, String

from .database import Base


class Demo(Base):
    __tablename__ = 'demos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default='')
    links_json = Column(Text, nullable=False, default='[]')
    tags_json = Column(Text, nullable=False, default='[]')
    image_path = Column(String(500), nullable=True)
    is_visible = Column(Boolean, nullable=False, default=True)
