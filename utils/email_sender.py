"""Gmail Dispatcher Module (SMTP TLS Integration).

Sends generated gospel posters and devotion text directly via Gmail.
- Embeds poster image inline (CID) and attaches as high-res PNG
- Elegant responsive HTML email template for mobile & desktop
- Defaults recipient to sender (GMAIL_USER) if RECEIVER_EMAILS is unset
"""

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from pathlib import Path
import smtplib
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def send_daily_poster_email(
    poster_path: Path,
    content: Dict[str, Any],
    church_name: str = "포이에마성령교회",
    gmail_user: Optional[str] = None,
    gmail_app_password: Optional[str] = None,
    receiver_emails: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    """Sends an email containing the poster image and devotional summary.

    Args:
        poster_path: Path to the generated poster PNG file
        content: Planned content dictionary (date_str, theme, headline, points, call_to_action)
        church_name: Church branding name
        gmail_user: Sender Gmail address (defaults to env GMAIL_USER)
        gmail_app_password: 16-character Gmail App Password (defaults to env GMAIL_APP_PASSWORD)
        receiver_emails: List of recipient addresses (defaults to sender if empty)

    Returns:
        (success: bool, message: str)
    """
    user = gmail_user or os.getenv("GMAIL_USER", "").strip()
    password = gmail_app_password or os.getenv("GMAIL_APP_PASSWORD", "").strip()

    if not user or not password:
        msg = "GMAIL_USER or GMAIL_APP_PASSWORD not set. Skipping email dispatch."
        logger.warning(msg)
        return False, msg

    poster_path = Path(poster_path)
    if not poster_path.exists():
        msg = f"Poster file not found at {poster_path}"
        logger.error(msg)
        return False, msg

    # Resolve recipients
    if receiver_emails:
        recipients = [r.strip() for r in receiver_emails if r.strip()]
    else:
        env_receivers = os.getenv("RECEIVER_EMAILS", "").strip()
        if env_receivers:
            recipients = [r.strip() for r in env_receivers.split(",") if r.strip()]
        else:
            recipients = [user]  # Send to self by default

    theme = content.get("theme", "말씀 묵상")
    date_str = content.get("date_str", "")
    headline = content.get("headline", "")
    sub_headline = content.get("sub_headline", "")
    cta = content.get("call_to_action", "")
    points = content.get("points", [])

    # Compose points HTML
    points_html = ""
    for idx, pt in enumerate(points, 1):
        p_title = pt.get("title", "") if isinstance(pt, dict) else getattr(pt, "title", "")
        p_desc = pt.get("description", "") if isinstance(pt, dict) else getattr(pt, "description", "")
        sc_obj = pt.get("scripture", {}) if isinstance(pt, dict) else getattr(pt, "scripture", {})
        sc_ref = sc_obj.get("reference", "") if isinstance(sc_obj, dict) else getattr(sc_obj, "reference", "")
        sc_txt = sc_obj.get("text", "") if isinstance(sc_obj, dict) else getattr(sc_obj, "text", "")

        points_html += f"""
        <div style="margin-bottom: 16px; padding: 14px 18px; background-color: #f8fafc; border-left: 4px solid #d4af37; border-radius: 6px;">
            <div style="font-size: 15px; font-weight: bold; color: #1e293b; margin-bottom: 6px;">
                <span style="display: inline-block; background-color: #d4af37; color: #ffffff; border-radius: 50%; width: 22px; height: 22px; text-align: center; line-height: 22px; font-size: 12px; margin-right: 6px;">{idx}</span>
                {p_title}
            </div>
            <div style="font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 8px;">{p_desc}</div>
            <div style="font-size: 13px; color: #0284c7; font-style: italic;">“{sc_txt}” <strong>({sc_ref})</strong></div>
        </div>
        """

    # Subject & HTML Body
    subject = f"[{church_name}] {date_str} 일간 말씀 포스터 - {headline}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Malgun Gothic', sans-serif; background-color: #f1f5f9; padding: 24px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            
            <!-- Header Banner -->
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 28px 24px; text-align: center; color: #ffffff;">
                <div style="font-size: 13px; color: #f5d062; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px;">
                    ✦ {church_name} 일간 말씀 묵상 ✦
                </div>
                <h1 style="margin: 0; font-size: 24px; color: #ffffff; font-weight: 700; line-height: 1.4;">
                    {headline}
                </h1>
                {f'<p style="margin: 8px 0 0 0; font-size: 14px; color: #e2e8f0;">{sub_headline}</p>' if sub_headline else ''}
            </div>

            <!-- Content Area -->
            <div style="padding: 24px;">
                <p style="font-size: 14px; color: #64748b; margin-top: 0;">
                    오늘 하루도 주님의 은혜와 성령의 충만하심이 삶의 모든 자리마다 가득하기를 축복합니다.
                </p>

                <!-- 3 Key Points -->
                {points_html}

                <!-- Call to Action -->
                <div style="background-color: #fefce8; border: 1px dashed #eab308; padding: 14px 18px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <span style="font-size: 14px; color: #854d0e; font-weight: 600;">“ {cta} ”</span>
                </div>

                <!-- Poster Image Inline -->
                <div style="text-align: center; margin: 24px 0;">
                    <p style="font-size: 13px; color: #94a3b8; margin-bottom: 8px;">▼ 오늘의 9:16 말씀 포스터 (모바일 배경화면 / 전도용)</p>
                    <img src="cid:poster_image" alt="오늘의 포스터" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;" />
                </div>
            </div>

            <!-- Footer -->
            <div style="background-color: #f8fafc; padding: 18px 24px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8;">
                {church_name} | 매일 아침 성령의 임재와 은혜의 말씀을 전합니다.<br/>
                본 메일은 자동 발송 시스템을 통해 발송되었습니다.
            </div>
        </div>
    </body>
    </html>
    """

    # Build MIME message
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"{church_name} <{user}>"
    msg["To"] = ", ".join(recipients)

    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    # Attach HTML
    msg_alt.attach(MIMEText(html_content, "html", "utf-8"))

    # Attach Poster Image (CID for inline rendering)
    with open(poster_path, "rb") as f:
        img_data = f.read()

    img_part = MIMEImage(img_data)
    img_part.add_header("Content-ID", "<poster_image>")
    img_part.add_header(
        "Content-Disposition", "inline", filename=poster_path.name
    )
    msg.attach(img_part)

    # Send via Gmail SMTP
    try:
        logger.info(f"Connecting to smtp.gmail.com:587 for {user}...")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.sendmail(user, recipients, msg.as_string())

        success_msg = (
            f"Successfully dispatched daily poster email to {', '.join(recipients)}"
        )
        logger.info(success_msg)
        return True, success_msg

    except Exception as e:
        err_msg = f"Failed to send email via Gmail SMTP: {e}"
        logger.error(err_msg)
        return False, err_msg


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Testing email module availability...")
    # Dry test without sending
    test_path = Path(__file__).resolve().parent.parent / "output" / "test_composed_poster.png"
    if test_path.exists():
        print(f"Test poster available: {test_path}")
    else:
        print("No test poster found.")
