import enum
from sqlalchemy import Table, Column, Integer, String, Boolean, func, Table, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

tags_pictures = Table('tags_pictures', Base.metadata,
                      Column('picture_id', Integer,
                             ForeignKey('pictures.id')),
                      Column('tag_id', Integer, ForeignKey('users.id'))
                      )


class Role(enum.Enum):
    __tablename__ = "roles"

    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(250), nullable=False)
    email = Column(String(150), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    role = Column('role', Enum(Role), default=Role.user, nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    pictures = relationship(
        "Picture",
        secondary=tags_pictures,
        backref="tags",
    )


class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    qr_code_url = Column(String(50), nullable=True)
    image_url = Column(String(50), nullable=False)
    tags = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship("User", backref="pictures", lazy="joined")
    tags = relationship(
        "Tag",
        secondary=tags_pictures,
        backref="pictures",
        passive_deletes=True
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"))
    user = relationship("User", backref="comments", lazy="joined")
    picture_id = Column(Integer, ForeignKey(Picture.id, ondelete="CASCADE"))
    picture = relationship("Picture", backref="comments", lazy="joined")
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime, default=func.now())
