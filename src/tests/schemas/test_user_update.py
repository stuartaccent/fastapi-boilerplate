import pytest
from pydantic import ValidationError

from app.api.schemas import UserUpdate


def test_is_valid():
    model = UserUpdate(
        email="me@example.com",
        password="password",
        first_name="some",
        last_name="one",
    )

    assert model.dict() == {
        "email": "me@example.com",
        "password": "password",
        "first_name": "some",
        "last_name": "one",
    }


def test_empty_is_valid():
    model = UserUpdate()

    assert model.dict(exclude_unset=True) == {}


@pytest.mark.parametrize(
    "data",
    [
        {
            "field": "email",
            "value": "not-an-email",
            "ex-msg": "value is not a valid email address",
            "ex-type": "value_error.email",
        },
        {
            "field": "password",
            "value": "pass",
            "ex-msg": "ensure this value has at least 6 characters",
            "ex-type": "value_error.any_str.min_length",
        },
        {
            "field": "first_name",
            "value": "x" * 121,
            "ex-msg": "ensure this value has at most 120 characters",
            "ex-type": "value_error.any_str.max_length",
        },
        {
            "field": "last_name",
            "value": "x" * 121,
            "ex-msg": "ensure this value has at most 120 characters",
            "ex-type": "value_error.any_str.max_length",
        },
    ],
)
def test_validation_errors(data):
    defaults = {data["field"]: data["value"]}

    with pytest.raises(ValidationError) as exc_info:
        UserUpdate(**defaults)

    error = exc_info.value.errors()[0]
    assert error["loc"] == (data["field"],)
    assert error["msg"] == data["ex-msg"]
    assert error["type"] == data["ex-type"]
