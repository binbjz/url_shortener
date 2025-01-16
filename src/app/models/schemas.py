from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator


class URLCreate(BaseModel):
    long_url: HttpUrl | str

    @classmethod
    @field_validator("long_url", mode="before")
    def convert_long_url_to_str(cls, values):
        if "long_url" in values and isinstance(values["long_url"], HttpUrl):
            values["long_url"] = str(values["long_url"])
        return values


class URLResponse(BaseModel):
    short_url: str
    long_url: HttpUrl | str
    created_at: Optional[int] = None

    @classmethod
    def from_raw(cls, short_url: str, long_url: HttpUrl | str,
                 created_at: Optional[int] = None):
        long_url_str = str(long_url) if isinstance(long_url, HttpUrl) else long_url
        return cls(short_url=short_url, long_url=long_url_str, created_at=created_at)


class URLInDB(URLResponse):
    id: str
    expires_at: Optional[int] = None
    access_count: int = Field(default=0, description="URL被访问的次数。")

