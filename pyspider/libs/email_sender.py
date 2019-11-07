# TEMPLATE FROM https://realpython.com/python-send-email/

import os, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender():
    def __init__(self):
        self._SENDER_EMAIL = "alert@pyspider.py"
        self._SMTP_HOST = os.environ['SMTP_HOST'] or 'localhost'
        self._SMTP_HOST = os.environ['SMTP_PORT'] or 25
        self._RECEIVER_EMAIL = os.environ['SMTP_EMAIL_ADDRESS'] or 'test@test.test'
        self._PASSWORD = os.environ['SMTP_EMAIL_PASSWORD'] or 'password'

    def __call__(self, *args, **kwargs):
        self.send_email(*args, **kwargs)

    def send_email(self, subject, text, html=None):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._SENDER_EMAIL
        message["To"] = self._RECEIVER_EMAIL

        # Turn param strings into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self._SMTP_HOST, 465, context=context) as server:
            server.login(self._RECEIVER_EMAIL, self._PASSWORD)
            server.sendmail(
                self._SENDER_EMAIL, self._RECEIVER_EMAIL, message.as_string()
            )