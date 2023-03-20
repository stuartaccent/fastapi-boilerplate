from fastapi import APIRouter

from app.authentication.dependencies import CurrentActiveUser, GetUserService
from app.authentication.schemas import UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_me(user: CurrentActiveUser):
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    user: CurrentActiveUser,
    user_service: GetUserService,
):
    return await user_service.update(user.id, data)
