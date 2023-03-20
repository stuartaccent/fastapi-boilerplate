from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, constr


class BearerResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    password: constr(min_length=6, max_length=120)


class UserCreate(BaseModel):
    email: EmailStr
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)
    password: constr(min_length=6, max_length=120)


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[constr(min_length=6, max_length=120)]
    first_name: Optional[constr(min_length=1, max_length=120)]
    last_name: Optional[constr(min_length=1, max_length=120)]


class UserUpdateFull(UserUpdate):
    is_active: Optional[bool]
    is_superuser: Optional[bool]
    is_verified: Optional[bool]


class VerifyToken(BaseModel):
    token: str


class VerifyRequest(BaseModel):
    email: EmailStr
