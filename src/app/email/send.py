from os.path import dirname, join, realpath
from typing import Any, Dict

import grpc
from starlette.templating import Jinja2Templates

from app.config import settings
from app.email.utils import minify_html
from app.grpc import grpc_clients
from protos.email_pb2 import EmailInfo, EmailRequest

dir_path = dirname(realpath(__file__))
email_templates = Jinja2Templates(directory=join(dir_path, "templates"))


async def send_email(
    to_address: str,
    subject: str,
    template_context: Dict[str, Any],
    template_name_html: str = None,
    template_name_text: str = None,
) -> bool:
    """constructs an email and sends it"""

    try:
        plain_text = ""
        if template_name_text:
            tmpl = email_templates.get_template(template_name_text)
            plain_text = tmpl.render(**template_context)
        html = ""
        if template_name_html:
            tmpl = email_templates.get_template(template_name_html)
            html = minify_html(tmpl.render(**template_context))

        email_info = EmailInfo(
            from_address=settings.email_from_address,
            to_address=to_address,
            subject=subject,
            plain_text=plain_text,
            html=html,
        )
        request = EmailRequest(email_info=email_info)
        await grpc_clients["email"].SendEmail(iter([request]))
    except grpc.aio.AioRpcError:
        return False

    return True
