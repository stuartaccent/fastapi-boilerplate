from typing import Optional
from uuid import UUID

from fastapi_users import schemas as users_schemas
from pydantic import EmailStr, constr


class UserCreate(users_schemas.CreateUpdateDictModel):
    email: EmailStr
    password: constr(min_length=6, max_length=120)
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)


class UserRead(users_schemas.CreateUpdateDictModel):
    id: UUID
    email: EmailStr
    first_name: constr(min_length=1, max_length=120)
    last_name: constr(min_length=1, max_length=120)
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        orm_mode = True


class UserUpdate(users_schemas.CreateUpdateDictModel):
    email: Optional[EmailStr]
    password: Optional[constr(min_length=6, max_length=120)]
    first_name: Optional[constr(min_length=1, max_length=120)]
    last_name: Optional[constr(min_length=1, max_length=120)]
