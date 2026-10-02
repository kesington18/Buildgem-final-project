import logging

logger = logging.getLogger("email_sender")


def send_otp_email(email: str, otp: str) -> None:
    """
    PLACEHOLDER: no real email service is configured for this project yet.
    For now this just logs the OTP so it can be read from `docker compose logs app`
    during testing. Replace this function's body with a real email provider
    (e.g. SendGrid, SMTP) when the team is ready.
    """
    logger.info(f"[OTP EMAIL — placeholder] To: {email} | Your admin signup OTP is: {otp}")