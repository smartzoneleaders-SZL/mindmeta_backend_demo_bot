import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# For env file
import os
from dotenv import load_dotenv
load_dotenv()

def send_email(receiver_email, subject, body):
    try:
        sender_email = "hello@notification.wheresit.ai"
        sender_name = "Mind Meta.ai"

        # Create a MIMEText email
        msg = MIMEMultipart()
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = receiver_email  
        msg["Subject"] = subject

        # Add the plain-text body to the email
        msg.attach(MIMEText(body, "plain"))

        # Send the email
        with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            server.starttls()
            server.login("api", "59a41c6480b9fe27a3f7510b892cd292")
            # Note: Use `receiver_email` (plain address) here
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"Email sent successfully to {receiver_email}")
        return True
    except Exception as e:
        return False