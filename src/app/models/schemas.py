from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class URLCreate(BaseModel):
    long_url: HttpUrl


class URLResponse(BaseModel):
    short_url: str
    long_url: HttpUrl
    created_at: Optional[int] = None


class URLInDB(URLResponse):
    id: str
    expires_at: Optional[int] = None
    access_count: int = Field(default=0, description="URL被访问的次数")
