from pydantic import BaseModel, ConfigDict
from typing import Optional
from sqlmodel import SQLModel
from pydantic import EmailStr
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)


class PostVote(BaseModel):
    post: PostResponse
    votes: int

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)


class UserCreate(SQLModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

    # class Config:
    #     from_attributes = True
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None


class Vote(BaseModel):
    post_id: int
