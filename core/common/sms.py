from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from django.conf import settings


def send_otp_to_phone(phone_number, otp):
    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )

        message = client.messages.create(
            body=f"Your OTP code is {otp}. It will expire in 5 minutes.",
            from_=settings.TWILIO_SMS_FROM,
            to=phone_number,
        )

        return message.sid

    except TwilioRestException as e:
        print(f"Twilio Error: {e}")
        return None
