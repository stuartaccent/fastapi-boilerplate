import pytest

from app.authentication.schemas import UserRead


@pytest.mark.asyncio
async def test_from_orm(user):
    model = UserRead.from_orm(user)

    assert model.dict() == {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
    }
