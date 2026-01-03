"""Email sending functionality using SMTP."""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
) -> None:
    """Send an email using SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email content

    Raises:
        Exception: If email sending fails
    """
    try:
        message = MIMEMultipart("alternative")
        message["From"] = (
            f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        )
        message["To"] = to_email
        message["Subject"] = subject

        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )

        logger.info(f"Email sent successfully to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise


async def send_invitation_email(
    to_email: str,
    invitation_token: str,
    invited_by_name: str,
) -> None:
    """Send an invitation email.

    Args:
        to_email: Invitee email address
        invitation_token: Secure invitation token
        invited_by_name: Name of person who sent the invitation
    """
    invitation_url = (
        f"{settings.FRONTEND_URL}/accept-invitation?token={invitation_token}"
    )

    # Load HTML template
    template_path = TEMPLATES_DIR / "invitation.html"
    if template_path.exists():
        html_content = template_path.read_text()
        html_content = html_content.replace(
            "{{invitation_url}}", invitation_url
        )
        html_content = html_content.replace(
            "{{invited_by_name}}", invited_by_name
        )
        html_content = html_content.replace("{{invitee_email}}", to_email)
    else:
        # Fallback inline template
        html_content = f"""
        <html>
        <body>
            <h2>You've been invited!</h2>
            <p>Hi,</p>
            <p>{invited_by_name} has invited you to join their organization.</p>
            <p>Click the link below to accept the invitation and create your account:</p>
            <p><a href="{invitation_url}">Accept Invitation</a></p>
            <p>This invitation will expire in 7 days.</p>
            <p>If you didn't expect this invitation, you can safely ignore this email.</p>
        </body>
        </html>
        """

    await send_email(
        to_email=to_email,
        subject="You've been invited to join our organization",
        html_content=html_content,
    )


async def send_welcome_email(
    to_email: str,
    first_name: str | None = None,
) -> None:
    """Send a welcome email to a new user.

    Args:
        to_email: User email address
        first_name: User's first name
    """
    name = first_name or to_email.split("@")[0]

    # Load HTML template
    template_path = TEMPLATES_DIR / "welcome.html"
    if template_path.exists():
        html_content = template_path.read_text()
        html_content = html_content.replace("{{user_name}}", name)
        html_content = html_content.replace(
            "{{frontend_url}}", settings.FRONTEND_URL
        )
    else:
        # Fallback inline template
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Business Operations!</h2>
            <p>Hi {name},</p>
            <p>Welcome to your new account! We're excited to have you on board.</p>
            <p>You can now log in and start using the platform:</p>
            <p><a href="{settings.FRONTEND_URL}/login">Go to Login</a></p>
            <p>If you have any questions, feel free to reach out to our support team.</p>
        </body>
        </html>
        """

    await send_email(
        to_email=to_email,
        subject="Welcome to Business Operations!",
        html_content=html_content,
    )


async def send_password_reset_email(
    to_email: str,
    reset_token: str,
) -> None:
    """Send a password reset email.

    Args:
        to_email: User email address
        reset_token: Password reset token
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    # Load HTML template
    template_path = TEMPLATES_DIR / "password_reset.html"
    if template_path.exists():
        html_content = template_path.read_text()
        html_content = html_content.replace("{{reset_url}}", reset_url)
        html_content = html_content.replace("{{user_email}}", to_email)
    else:
        # Fallback inline template
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi,</p>
            <p>We received a request to reset your password.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
        </body>
        </html>
        """

    await send_email(
        to_email=to_email,
        subject="Password Reset Request",
        html_content=html_content,
    )
