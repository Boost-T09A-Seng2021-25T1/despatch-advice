import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import logging
from dotenv import load_dotenv

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env vars
load_dotenv(dotenv_path=os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config")),
    ".env"
))

async def send_despatch_email(recipient_email, subject, body, attachment=None):
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            raise ValueError("Missing sender email/password environment variables")

        # Build email
        message = MIMEMultipart()
        message["From"] = f"BoostXchange <{sender_email}>"
        message["To"] = recipient_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        if attachment:
            filename, content = attachment
            part = MIMEApplication(content)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            message.attach(part)

        # Send
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            username=sender_email,
            password=sender_password,
            start_tls=True,
            timeout=15
        )

        logger.info(f"Email sent to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        return False




def create_despatch_email_body(despatch_data):
    """
    Create HTML email body for despatch notification

    Args:
        despatch_data (dict): Despatch advice data

    Returns:
        str: HTML email body
    """
    # Extract relevant information from despatch data
    despatch_id = despatch_data.get("ID", "")
    issue_date = despatch_data.get("IssueDate", "")

    # Create an HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif;
            line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #f8f9fa; padding: 15px;
            border-radius: 5px; margin-bottom: 20px; }}
            .header h1 {{ color: #333366; margin: 0; }}
            .content {{ padding: 15px; background-color: #fff;
            border-radius: 5px; }}
            .footer {{ margin-top: 20px; font-size: 12px; color: #999;
            text-align: center; }}
            .button {{ display: inline-block; padding: 10px 20px;
            background-color: #4CAF50; color: white;
                      text-decoration: none; border-radius:
                      5px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Despatch Advice Notification</h1>
            </div>
            <div class="content">
                <p>A new despatch advice has been generated for your order.</p>
                <p><strong>Despatch ID:</strong> {despatch_id}</p>
                <p><strong>Issue Date:</strong> {issue_date}</p>
                <p>Please find the attached despatch advice document
                for your records.</p>
                <p>If you have any questions regarding this shipment,
                please contact our customer service team.</p>
                <a href="#" class="button">View Despatch Details</a>
            </div>
            <div class="footer">
                <p>This is an automated message.
                Please do not reply to this email.</p>
                <p>&copy; 2025 BoostXchange. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_body
