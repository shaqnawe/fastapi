from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr
from datetime import datetime, timezone


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str = Field(index=True)
    published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: int = Field(foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="posts")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: EmailStr = Field(default=None, unique=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    posts: list["Post"] = Relationship(back_populates="user")


class Vote(SQLModel, table=True):
    __tablename__ = "votes"

    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE", primary_key=True)
    post_id: int = Field(foreign_key="posts.id", ondelete="CASCADE", primary_key=True)
