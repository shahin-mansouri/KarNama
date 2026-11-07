from bale import Bot
from django.conf import settings
import asyncio


TOKEN = settings.BALE_TOKEN
CHANNEL_ID = "@karnamma"
# client = Bot(token=TOKEN)


client = Bot(token=TOKEN)


def send_message(MESSAGE):


    @client.event
    async def on_ready():
        try:
            await client.send_message(CHANNEL_ID, MESSAGE)
            print("Message sent successfully!")

        except Exception as e:
            print(f"Error sending message: {e}")

        finally:
            await client.close()


    client.run()


