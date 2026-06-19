import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_contact_notification(name: str, email: str, phone: str, message: str) -> bool:
    """
    Send an email notification to the admin when a contact form is submitted.
    Returns True on success, False on failure.
    """
    if not settings.SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD is not set — skipping email notification.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Contact Message from {name} — New Face Furniture"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = settings.SMTP_FROM_EMAIL  # notify the same inbox
        msg["Reply-To"] = email               # reply goes directly to the customer

        # ── Plain text fallback ───────────────────────────────────────────────
        plain = f"""
New contact message received on New Face Furniture website.

Name:    {name}
Email:   {email}
Phone:   {phone or 'Not provided'}
Message:
{message}
        """.strip()

        # ── HTML version ─────────────────────────────────────────────────────
        html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
    .container {{ background: #ffffff; max-width: 600px; margin: auto; border-radius: 8px;
                  padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
    .header {{ border-bottom: 3px solid #c9a84c; padding-bottom: 16px; margin-bottom: 24px; }}
    .header h1 {{ margin: 0; font-size: 22px; color: #1a1a1a; }}
    .field {{ margin-bottom: 16px; }}
    .label {{ font-size: 12px; font-weight: bold; color: #888; text-transform: uppercase;
              letter-spacing: 0.5px; margin-bottom: 4px; }}
    .value {{ font-size: 15px; color: #1a1a1a; }}
    .message-box {{ background: #f9f9f9; border-left: 4px solid #c9a84c; padding: 16px;
                    border-radius: 4px; font-size: 15px; color: #333; line-height: 1.6; }}
    .footer {{ margin-top: 32px; font-size: 12px; color: #aaa; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📬 New Contact Message</h1>
      <p style="margin:8px 0 0; color:#666; font-size:14px;">Received via New Face Furniture website</p>
    </div>

    <div class="field">
      <div class="label">Name</div>
      <div class="value">{name}</div>
    </div>

    <div class="field">
      <div class="label">Email</div>
      <div class="value"><a href="mailto:{email}" style="color:#c9a84c;">{email}</a></div>
    </div>

    <div class="field">
      <div class="label">Phone</div>
      <div class="value">{phone or 'Not provided'}</div>
    </div>

    <div class="field">
      <div class="label">Message</div>
      <div class="message-box">{message.replace(chr(10), '<br>')}</div>
    </div>

    <div class="footer">
      New Face Furniture &mdash; info@newfacefurniture.co.ke
    </div>
  </div>
</body>
</html>
        """.strip()

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, settings.SMTP_FROM_EMAIL, msg.as_string())

        logger.info(f"Contact notification email sent for: {email}")
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check SMTP_USERNAME and SMTP_PASSWORD in .env")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending contact notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending contact notification: {e}")
        return False


def send_contact_auto_reply(name: str, email: str) -> bool:
    """
    Send an auto-reply acknowledgement to the customer after they submit the contact form.
    Returns True on success, False on failure.
    """
    if not settings.SMTP_PASSWORD:
        logger.warning("SMTP_PASSWORD is not set — skipping auto-reply.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "We've received your message — New Face Furniture"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = email

        plain = f"""
Hi {name},

Thank you for reaching out to New Face Furniture!

We've received your message and will get back to you within 24 hours.

In the meantime, feel free to browse our collection at https://newfacefurniture.co.ke
or reach us directly on WhatsApp for faster assistance.

Warm regards,
New Face Furniture Team
info@newfacefurniture.co.ke
        """.strip()

        html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
    .container {{ background: #ffffff; max-width: 600px; margin: auto; border-radius: 8px;
                  padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
    h2 {{ color: #1a1a1a; margin-top: 0; }}
    p {{ color: #444; line-height: 1.7; font-size: 15px; }}
    .cta {{ display: inline-block; margin-top: 16px; padding: 12px 28px;
            background: #c9a84c; color: #fff; text-decoration: none;
            border-radius: 4px; font-weight: bold; font-size: 14px; }}
    .footer {{ margin-top: 32px; font-size: 12px; color: #aaa; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <h2>Hi {name}, we've got your message! 👋</h2>
    <p>
      Thank you for reaching out to <strong>New Face Furniture</strong>.
      We've received your enquiry and one of our team members will get back to you
      within <strong>24 hours</strong>.
    </p>
    <p>
      In the meantime, feel free to explore our latest furniture collection:
    </p>
    <a href="https://newfacefurniture.co.ke" class="cta">View Our Collection</a>
    <p style="margin-top:24px;">
      For faster assistance, you can also reach us directly on WhatsApp.
    </p>
    <p>Warm regards,<br><strong>New Face Furniture Team</strong></p>
    <div class="footer">
      New Face Furniture &mdash; info@newfacefurniture.co.ke &mdash; Nairobi, Kenya
    </div>
  </div>
</body>
</html>
        """.strip()

        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, email, msg.as_string())

        logger.info(f"Auto-reply sent to: {email}")
        return True

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending auto-reply: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending auto-reply: {e}")
        return False