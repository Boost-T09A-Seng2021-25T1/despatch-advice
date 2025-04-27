import json
import os
import logging
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables (no need to load 
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type"
}

async def send_despatch_email(recipient_email, subject, body, attachment=None):
    """
    Send an email with optional attachment.
    """
    try:
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            raise ValueError("Missing sender email/password environment variables")

        message = MIMEMultipart()
        message["From"] = f"BoostXchange <{SENDER_EMAIL}>"
        message["To"] = recipient_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "html"))

        if attachment:
            filename, content = attachment
            part = MIMEApplication(content)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            message.attach(part)

        await smtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD,
            start_tls=True,
            timeout=15
        )

        logger.info(f"Email sent to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        return False

def create_despatch_email_body(despatch_info):
    """
    Create HTML email body for despatch notification.
    """
    despatch_id = despatch_info.get("ID", "Unknown")
    issue_date = despatch_info.get("IssueDate", "Unknown")

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .header h1 {{ color: #333366; }}
        .content {{ background-color: #fff; padding: 15px; border-radius: 5px; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #999; text-align: center; }}
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
          <p>Please find the attached despatch advice document for your records.</p>
        </div>
        <div class="footer">
          <p>This is an automated message. Please do not reply.</p>
          <p>&copy; 2025 BoostXchange</p>
        </div>
      </div>
    </body>
    </html>
    """
    return html_body


def lambda_handler(event, context):
    try:
        #debugging
        logger.info("Lambda started")

        body = json.loads(event.get("body", "{}"))
        recipient_email = body.get("recipient_email")
        subject = body.get("subject", "Despatch Advice")
        despatch_info = body.get("despatch_info", {})
        despatch_xml_base64 = body.get("despatch_xml")

        if not recipient_email or not despatch_xml_base64:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "Missing required fields"})
            }

        despatch_xml_bytes = base64.b64decode(despatch_xml_base64)

        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email
        message["Subject"] = subject

        body_html = f"""
        <!DOCTYPE html>
        <html>
            <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .header h1 {{ color: #333366; }}
                .content {{ background-color: #fff; padding: 15px; border-radius: 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #999; text-align: center; }}
            </style>
            </head>
            <body>
                <div class="container">
                <div class="header">
                    <h1>Despatch Advice Notification</h1>
                </div>
                <div class="content">
                    <p>A new despatch advice has been generated for your order.</p>
                    <p><strong>Despatch ID:</strong> {despatch_info.get('ID', '')}</p>
                    <p><strong>Issue Date:</strong> {despatch_info.get('IssueDate', '')}</p>
                    <p>Please find the attached despatch advice document for your records.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply.</p>
                    <p>&copy; 2025 BoostXchange</p>
                </div>
                </div>
            </body>
        </html>
        """

        message.attach(MIMEText(body_html, "html"))

        attachment = MIMEApplication(despatch_xml_bytes, Name="DespatchAdvice.xml")
        attachment['Content-Disposition'] = 'attachment; filename="DespatchAdvice.xml"'
        message.attach(attachment)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(message)

        logger.info(f"Email successfully sent to {recipient_email}")

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "Email sent successfully"})
        }

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }