import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


import os

# Function to send email alert
def send_email_alert(suspected_message, recipient_email):
    sender_email = os.getenv('EMAIL_SENDER')
    sender_password = os.getenv('EMAIL_PASSWORD')

    if not sender_email or not sender_password:
        raise ValueError("Missing EMAIL_SENDER or EMAIL_PASSWORD in environment variables")
    
    if not recipient_email:
        raise ValueError("Recipient email is missing or None")

    print(f"📧 Sending email from {sender_email} to {recipient_email}")  # Debugging

    subject = "Urgent: Concerning Message Detected"
    body = f"""
    Warning: A concerning message was detected that may indicate self-harm or harm to others.
    
    Suspected message:
    "{suspected_message}"

    Please check on the user immediately.
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT'))
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("✅ Email alert sent successfully.")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        raise
