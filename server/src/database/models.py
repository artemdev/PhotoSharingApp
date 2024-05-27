from sqlalchemy import Table, Column, Integer, String, ForeignKey, Enum, DateTime, func, Boolean
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# Association table for many-to-many relationship between pictures and tags
tags_pictures = Table('tags_pictures', Base.metadata,
    Column('picture_id', Integer, ForeignKey('pictures.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Role(enum.Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(250), nullable=False)
    avatar = Column(String(255), nullable=True)
    email = Column(String(150), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    role = Column(Enum(Role), default=Role.user, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed = Column(Boolean, default=False, nullable=True)

    pictures = relationship("Picture", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True, index=True)
    qr_code_url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    user = relationship("User", back_populates="pictures")
    tags = relationship(
        "Tag",
        secondary=tags_pictures,
        back_populates="pictures",
        passive_deletes=True
    )
    comments = relationship('Comment', back_populates='picture', cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    picture_id = Column(Integer, ForeignKey('pictures.id', ondelete="CASCADE"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="comments")
    picture = relationship("Picture", back_populates="comments")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

    pictures = relationship(
        "Picture",
        secondary=tags_pictures,
        back_populates="tags"
    )
