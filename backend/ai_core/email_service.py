"""
Email service for sending verification codes
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from ai_core.config import settings
from ai_core.logger import logger


async def send_verification_code(to_email: str, code: str) -> bool:
    """
    Send verification code via SendGrid
    """
    try:
        if not settings.SENDGRID_API_KEY:
            logger.warning("SendGrid not configured, code would be: " + code)
            return True
        
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=to_email,
            subject='Thespis Developer Verification Code',
            html_content=f"""
            <html>
                <body>
                    <h2>Thespis AI - Developer Access</h2>
                    <p>Your verification code is:</p>
                    <h1 style="color: #1976d2; letter-spacing: 5px;">{code}</h1>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you did not request this code, please ignore this email.</p>
                </body>
            </html>
            """
        )
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Verification code sent to {to_email}, status: {response.status_code}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
