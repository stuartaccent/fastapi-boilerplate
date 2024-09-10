from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Attachment(_message.Message):
    __slots__ = ["content_type", "data", "filename"]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    content_type: str
    data: bytes
    filename: str
    def __init__(self, filename: _Optional[str] = ..., data: _Optional[bytes] = ..., content_type: _Optional[str] = ...) -> None: ...

class EmailInfo(_message.Message):
    __slots__ = ["from_address", "html", "plain_text", "subject", "to_address"]
    FROM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    PLAIN_TEXT_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    TO_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    from_address: str
    html: str
    plain_text: str
    subject: str
    to_address: str
    def __init__(self, from_address: _Optional[str] = ..., to_address: _Optional[str] = ..., subject: _Optional[str] = ..., plain_text: _Optional[str] = ..., html: _Optional[str] = ...) -> None: ...

class EmailRequest(_message.Message):
    __slots__ = ["attachment", "email_info"]
    ATTACHMENT_FIELD_NUMBER: _ClassVar[int]
    EMAIL_INFO_FIELD_NUMBER: _ClassVar[int]
    attachment: Attachment
    email_info: EmailInfo
    def __init__(self, email_info: _Optional[_Union[EmailInfo, _Mapping]] = ..., attachment: _Optional[_Union[Attachment, _Mapping]] = ...) -> None: ...

class EmailResponse(_message.Message):
    __slots__ = ["message", "success"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    message: str
    success: bool
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
