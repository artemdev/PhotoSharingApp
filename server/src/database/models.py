import enum
from sqlalchemy import Table, Column, Integer, String, Boolean, func, Table, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

tags_pictures = Table('tags_pictures', Base.metadata,
                      Column('picture_id', Integer, ForeignKey('pictures.id', ondelete="CASCADE")),
                      Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
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
    name = Column(String(50), nullable=False, unique=True)
    pictures = relationship(
        "Picture",
        secondary=tags_pictures,
        back_populates="tags",
    )


class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True, index=True)
    qr_code_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    description = Column(String, nullable=True)
    user = relationship("User", back_populates="pictures")
    tags = relationship(
        "Tag",
        secondary=tags_pictures,
        back_populates="pictures",
        passive_deletes=True
    )
    comments = relationship('Comment', back_populates='picture')


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    picture_id = Column(Integer, ForeignKey('pictures.id', ondelete="CASCADE"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="comments")
    picture = relationship("Picture", back_populates="comments")
