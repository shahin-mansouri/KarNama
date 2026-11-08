from bale import Bot
from django.conf import settings


TOKEN = settings.BALE_TOKEN
CHANNEL_ID = "@karnamma"


def send_message(message):
    client = Bot(token=TOKEN)

    @client.event
    async def on_ready():
        try:
            await client.send_message(CHANNEL_ID, message)
            print("Message sent successfully!")

        except Exception as e:
            print(f"Error sending message: {e}")

        finally:
            await client.close()


    client.run()

