import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import getLogger
from os import getenv

from core.config import settings

# def send_email(subject: str, body: str, receiver_email: str) -> None:
#     """
#     Sends an email to a receiver

#     Args:
#         subject: the email subject
#         body: the email body
#         receiver_email: the receiver email
#     """
#     logger = getLogger(__name__)
#     sender_email = settings.SMTP_USERNAME
#     sender_password = settings.SMTP_PASSWORD
#     server = settings.SMTP_SERVER
#     port = settings.SMTP_PORT

#     html_body = body
#     # Set up the MIME
#     email_msg = MIMEMultipart()
#     email_msg["From"] = sender_email
#     email_msg["To"] = receiver_email
#     email_msg["Subject"] = subject

#     # Attach the message to the email
#     email_msg.attach(MIMEText(html_body, "html"))

#     context = ssl.create_default_context()

#     # Try to log in to server and send email
#     try:
#         logger.info("Started SMTP")
#         server = smtplib.SMTP(mail_server, port)
#         server.ehlo()
#         server.starttls(context=context)  # Secure the connection
#         server.ehlo()
#         server.login(sender_email, sender_password)
#         text = email_msg.as_string()
#         server.sendmail(sender_email, receiver_email, text)
#         logger.info("Sent email")
#     except Exception as ex:
#         logger.error(ex)
#         raise ex
#     finally:
#         logger.info("SMTP quit")
#         server.quit()


def send_email(subject: str, body: str, receiver_email: str) -> None:
    """
    Sends an email to a receiver

    Args:
        subject: the email subject
        body: the email body
        receiver_email: the receiver email
    """
    logger = getLogger(__name__ + ".send_email")
    try:
        sender_email = settings.SMTP_USERNAME
        sender_password = settings.SMTP_PASSWORD
        server = settings.SMTP_SERVER
        port = settings.SMTP_PORT

        html_body = body
        # Set up the MIME
        email_msg = MIMEMultipart()
        email_msg["From"] = sender_email
        email_msg["To"] = receiver_email
        email_msg["Subject"] = subject

        # Attach the message to the email
        email_msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(server, port, context=context) as server:
            server.login(sender_email, sender_password)
            text = email_msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
    except Exception as ex:
        logger.error(ex)
        raise ex


def send_email_verification(receiver_email: str, token: str) -> None:

    url = f"{getenv('VERIFY_EMAIL_URL')}?token={token}"
    sender_email = getenv("EMAIL_ACCOUNT")
    subject = "Mannequins Email Verification"
    html_body = f"""
<html>
  <body>
    <p>Hello,</p>
    <p>Click on this <a href="{url}">Verify Email</a> to verify your email.</p>
    <p>For more information contact: <a href="mailto:{sender_email}">{sender_email}</a></p>
    <p>Best regards,<br>
    The Mannequins Team</p>
  </body>
</html>
"""
    send_email(subject, html_body, receiver_email)


def send_reset_email(receiver_email: str, token: str) -> None:

    url = f"{getenv('RESET_PASSWORD_URL')}?token={token}"
    sender_email = getenv("EMAIL_ACCOUNT")
    subject = "Mannequins Password Reset"
    html_body = f"""
<html>
  <body>
    <p>Hello,</p>
    <p>Click on this <a href="{url}">Reset Password</a> to reset your password.</p>
    <p>For more information contact: <a href="mailto:{sender_email}">{sender_email}</a></p>
    <p>Best regards,<br>
    The Mannequins Team</p>
  </body>
</html>
"""
    send_email(subject, html_body, receiver_email)
