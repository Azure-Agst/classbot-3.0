import os
import socket
import requests
import __main__
from enum import Enum
from datetime import datetime

BOT_NAME = "fsu-classbot"
BOT_PFP_URL = ""

class DiscordNotifier():
    """Main Discord Webhook Post Class"""

    class Colors(int, Enum):
        """Main Color Enum, used in Discord embeds"""

        # If you havent noticed already, yes this is literally
        # getbootstrap.com's button color scheme, lmfao
        
        PRIMARY = int(0x0069d9)
        SECONDARY = int(0x5a6268)
        SUCCESS = int(0x218838)
        DANGER = int(0xc82333)
        WARNING = int(0xe0a800)
        INFO = int(0x138496)
        LIGHT = int(0xe2e6ea)
        DARK = int(0x23272b) 

    def __init__(
        self, 
        url: str, 
        pings: str = None
        ):
        """Constructor"""

        # Save local vars
        self.url = url
        self.pings = pings

        # Error checking
        if not self.url:
            raise Exception("Must have post URL!")

    def send_embed(
        self, 
        title: str, 
        message: str,
        image: list = None,
        color: int = Colors.PRIMARY
        ):
        """Main Discord Message Function"""

        # get main file name
        entrypoint = os.path.basename(__main__.__file__)

        # format message contents
        embed = {
            "username": BOT_NAME,
            "avatar_url": BOT_PFP_URL,
            "content": self.pings if not None else "",
            "embeds": [
                {
                    "title": title,
                    "description": message,
                    "color": color,
                    "timestamp": str(datetime.utcnow().isoformat()),
                    "footer": {
                        "text": f"{entrypoint} on '{socket.gethostname()}'"
                    }
                }
            ]
        }

        # add images, if applicable
        if image:
            embed['embeds'][0]['image'] = {
                "url": image
            }

        # send embed
        requests.post(self.url, json=embed)