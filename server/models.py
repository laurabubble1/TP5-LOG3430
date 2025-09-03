from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    post_count: int
    follower_count: int
    following_count: int
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    author_username: str
    created_at: datetime = Field(default_factory=datetime.now)
    likes: int = 0
    
    class Config:
        from_attributes = True