


from .models import User
from twilio.rest import Client

MAX_TEXTS_PER_ACCOUNT = 100


def send_text(to,message):
    obj = User.objects.get(phone_num=to)
    if obj.pins_sent < MAX_TEXTS_PER_ACCOUNT:
        account_sid = 'AC4253ac2fc098bda1942fe5a909b8588e'
        auth_token = '8719d4cdea72bec120e16bb7aef9e678'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            messaging_service_sid='MGf469f3b069d1008e337e65ed3fe9a062',
            body=("RUF Assassins: " + message),   
            to='+1' + str(to)
        )
    obj.pins_sent = obj.pins_sent + 1
    obj.save()