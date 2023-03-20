import pytest
from pydantic import ValidationError

from app.authentication.schemas import UserCreate


def test_is_valid():
    model = UserCreate(
        email="me@example.com",
        password="password",
        first_name="some",
        last_name="one",
    )

    assert model.dict() == {
        "email": "me@example.com",
        "first_name": "some",
        "last_name": "one",
        "password": "password",
    }


def test_required_values():
    with pytest.raises(ValidationError) as exc_info:
        UserCreate()

    expected = [
        {
            "loc": ("email",),
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ("first_name",),
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ("last_name",),
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ("password",),
            "msg": "field required",
            "type": "value_error.missing",
        },
    ]

    assert exc_info.value.errors() == expected


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
            "value": "",
            "ex-msg": "ensure this value has at least 6 characters",
            "ex-type": "value_error.any_str.min_length",
        },
        {
            "field": "first_name",
            "value": "",
            "ex-msg": "ensure this value has at least 1 characters",
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
            "value": "",
            "ex-msg": "ensure this value has at least 1 characters",
            "ex-type": "value_error.any_str.min_length",
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
    defaults = {
        "email": "me@example.com",
        "password": "password",
        "first_name": "some",
        "last_name": "one",
    }
    defaults[data["field"]] = data["value"]

    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**defaults)

    error = exc_info.value.errors()[0]
    assert error["loc"] == (data["field"],)
    assert error["msg"] == data["ex-msg"]
    assert error["type"] == data["ex-type"]
