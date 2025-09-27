import smtplib
import importlib
import pkgutil
import secrets

from email.message import EmailMessage
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from bson.objectid import ObjectId
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.dependencies import env

def convert_datetime_to_gmt(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class AppModel(BaseModel):
    class Config:
        json_encoders = {datetime: convert_datetime_to_gmt, ObjectId: str}
        arbitrary_types_allowed = True
        validate_by_name = True


def import_routers(package_name):
    package = importlib.import_module(package_name)
    prefix = package.__name__ + "."

    for _, module_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        if not module_name.startswith(prefix + "router_"):
            continue

        try:
            importlib.import_module(module_name)
        except Exception as e:
            print(f"Failed to import {module_name}, error: {e}")
            

def send_email(subject: str, email: str, custom_message: str) -> str:
    smtp_server = env.smtp_server
    smtp_port = env.smtp_port
    smtp_user=env.smtp_email
    smtp_password = env.smtp_password
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = email
    msg.set_content("Your email client does not support HTML.")
    msg.add_alternative(custom_message, subtype="html")

    # Send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_user, smtp_password)
            smtp.send_message(msg)
        return(f"Email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error in sending email. Check the Internet Connection.",
        )
        
def generate_otp(length=6):
    return ''.join(secrets.choice("0123456789") for _ in range(length))

def get_current_utc_time():
    return datetime.now(tz=timezone.utc)