from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import dirname, join, realpath
from typing import Any, Dict

from accentnotifications.manager import NotificationManager
from accentnotifications.notifications import SmtpNotification
from starlette.templating import Jinja2Templates

from app.config import settings

dir_path = dirname(realpath(__file__))
email_templates = Jinja2Templates(directory=join(dir_path, "templates"))


async def generate_email(
    to_address: str,
    subject: str,
    template_context: Dict[str, Any],
    template_name_html: str = None,
    template_name_text: str = None,
) -> bool:
    """constructs an email and sends it"""

    email = MIMEMultipart("alternative")
    email["From"] = settings.email_from_address
    email["To"] = to_address
    email["Subject"] = subject
    if template_name_html:
        tmpl = email_templates.get_template(template_name_html)
        content_html = tmpl.render(**template_context)
        email.attach(MIMEText(content_html, "html", _charset="utf-8"))
    if template_name_text:
        tmpl = email_templates.get_template(template_name_text)
        content_text = tmpl.render(**template_context)
        email.attach(MIMEText(content_text, "plain", _charset="utf-8"))

    # send the email
    notification = SmtpNotification(email=email, fail_silently=False)
    return await NotificationManager().send(notification)
