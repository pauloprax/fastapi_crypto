import os
from twilio.rest import Client as TwilioClient

twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_to_number = os.environ.get('TWILIO_TO_NUMBER')
twilio_messaging_service_sid = os.environ.get('TWILIO_MESSAGING_SERVICE_SID')


class NotificationGateway:
    def __init__(self):
        self.twilio_client = TwilioClient(
            twilio_account_sid, twilio_auth_token)

    def send_message(self, message):
        message = self.twilio_client.messages.create(
            messaging_service_sid=twilio_messaging_service_sid,
            body=message,
            to=twilio_to_number
        )
        if message.sid:
            return True
        return False


class Notification:
    def __init__(self, message):
        self.message = message
        self.notification_gateway = NotificationGateway()

    def __str__(self):
        return f"Message: {self.message}"

    def __repr__(self):
        return f"Message: {self.message}"

    def send(self):
        return self.notification_gateway.send_message(self.message)
