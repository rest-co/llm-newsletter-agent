import smtplib
import os

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")


load_dotenv()

def send_email(to_emails, subject, html_content):
    sender_email = os.getenv("NAVER_EMAIL")
    sender_password = os.getenv("NAVER_PASSWORD")

    if isinstance(to_emails, str):
        to_emails = [email.strip() for email in to_emails.split(",")]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(to_emails)

    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)

    server = smtplib.SMTP("smtp.naver.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)

    server.sendmail(
        sender_email,
        to_emails,
        msg.as_string()
    )

    server.quit()

    print("메일 발송 완료")



