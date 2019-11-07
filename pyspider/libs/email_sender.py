# TEMPLATE FROM https://realpython.com/python-send-email/

import os, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender():
    def __init__(self, *args, **kwargs):
        self._SENDER_EMAIL = "alert@pyspider.py"
        self._SMTP_HOST = os.environ.get('SMTP_HOST') or 'localhost'
        self._SMTP_PORT = os.environ.get('SMTP_PORT') or 587
        self._RECEIVER_EMAIL = os.environ.get('SMTP_EMAIL_ADDRESS') or 'test@test.test'
        self._PASSWORD = os.environ.get('SMTP_EMAIL_PASSWORD') or None
        self.send_email(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.send_email(*args, **kwargs)

    def send_email(self, subject, text, html=None):
        if html is None:
            html = ''
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
        with smtplib.SMTP(self._SMTP_HOST, self._SMTP_PORT) as server:
            server.connect(self._SMTP_HOST, self._SMTP_PORT)
            server.ehlo()
            if self._PASSWORD is not None:
                server.login(self._RECEIVER_EMAIL, self._PASSWORD)
            server.sendmail(
                self._SENDER_EMAIL, self._RECEIVER_EMAIL, message.as_string()
            )