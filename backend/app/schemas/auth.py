from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: str = ""

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    password: str
