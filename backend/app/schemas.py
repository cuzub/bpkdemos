from pydantic import BaseModel, Field, HttpUrl


class DemoLink(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    url: HttpUrl


class DemoBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = ''
    links: list[DemoLink] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    image_path: str | None = None
    is_visible: bool = True


class DemoCreate(DemoBase):
    pass


class DemoUpdate(DemoBase):
    pass


class DemoRead(DemoBase):
    id: int


class VisibilityPayload(BaseModel):
    is_visible: bool


class LoginPayload(BaseModel):
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
