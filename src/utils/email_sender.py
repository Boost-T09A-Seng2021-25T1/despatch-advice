import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config")),
    ".env"
    )
)


async def send_despatch_email(recipient_email, subject, body, attachment=None):
    """
    Send an email with optional attachment

    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Email subject
        body (str): Email body (HTML format)
        attachment (tuple, optional): Tuple of (filename, file_content_bytes)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email configuration (from environment variables)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            raise ValueError(
                "Email credentials not configured in environment variables"
            )

        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Add body
        message.attach(MIMEText(body, "html"))

        # Add attachment if provided
        if attachment:
            filename, content = attachment
            part = MIMEApplication(content, Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            message.attach(part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            username=sender_email,
            password=sender_password,
            use_tls=True
        )

        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
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
