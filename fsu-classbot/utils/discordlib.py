import socket
import requests
from enum import Enum
from datetime import datetime

# These should be imported from wherever
from ..version import __version__

BOT_NAME = "fsu-classbot"
BOT_PFP_URL = ""

class DiscordNotifier():
    """Main Discord Webhook Post Class"""

    url_base = "https://discord.com/api/webhooks"

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

    def __init__(self, url: str, pings: str = None):
        """TODO: Important text goes here"""

        # Error checking
        if not url:
            raise Exception("Must have post URL!")

        # Check if this is a valid url
        if not url.startswith(self.url_base):
            raise Exception("Invalid webhook, wtf?")

        # Split webhook into parts
        self.id, self.token = \
            url.replace(self.url_base, "") \
            .split("?")[0] \
            .split("/")[1:]

        # Save pings
        self.pings = pings

    #
    # Sends
    #

    def send_message(self, content: str):
        """Main Discord Message Function"""

        return requests.post(
            f"{self.url_base}/{self.id}/{self.token}?wait=true",
            json=self._format_json(
                contents=content
            )
        ).json()

    def send_embed(self, title: str, description: str,
        image: str = None, color: int = Colors.PRIMARY):
        """Main *Pretty* Discord Message Function"""

        return requests.post(
            f"{self.url_base}/{self.id}/{self.token}?wait=true",
            json=self._format_json(
                e_title=title,
                e_description=description,
                e_color=color,
                e_image=image
            )
        ).json()

    #
    # Updates
    #

    def update_message(self, message: dict, content: str):
        """Updates a message in a Discord channel"""

        # get the message id
        message_id = message['id']

        # get updates
        new_content = content if content is not None else message['content']

        # update the message
        return requests.patch(
            f"{self.url_base}/{self.id}/{self.token}/messages/{message_id}",
            json=self._format_json(
                contents=new_content
            )
        ).json()

    def update_embed(self, message: dict, 
        title: str = None, description: str = None,
        image: str = None, color: int = None):
        """Updates an embed in a Discord channel"""

        # get the message id
        message_id = message['id']

        # get updates
        new_title = title if title is not None \
            else message['embeds'][0]['title']
        new_description = description if description is not None \
            else message['embeds'][0]['description']
        new_image = image if image is not None \
            else message['embeds'][0]['image']['url'] if 'image' in message['embeds'][0] \
            else None
        new_color = color if color is not None \
            else message['embeds'][0]['color']
        
        return requests.patch(
            f"{self.url_base}/{self.id}/{self.token}/messages/{message_id}",
            json=self._format_json(
                e_title=new_title,
                e_description=new_description,
                e_image=new_image,
                e_color=new_color
            )
        ).json()

    #
    # Deletes
    #

    def delete_message(self, message: dict):
        """Deletes a message in a Discord channel"""
        
        # get the message id
        message_id = message['id']
        
        # delete the message
        return requests.delete(
            f"{self.url_base}/{self.id}/{self.token}/messages/{message_id}"
        )
    
    #
    # Helpers
    #

    def _format_json(
        self, 
        contents: str = "",
        e_title: str  = "",
        e_description: str = "",
        e_image: str = None,
        e_color: int = Colors.PRIMARY
        ):
        """Formats the json for the webhook"""

        # start with a clean json
        json = {}

        # add username and pfp
        json['username'] = BOT_NAME
        json['avatar_url'] = BOT_PFP_URL

        # add pings and contents
        if self.pings:
            json['content'] = self.pings + " " + contents
        else:
            json['content'] = contents

        # if e_title or e_description is not empty, add embed
        if e_title or e_description:
            json['embeds'] = [
                {
                    "title": e_title,
                    "description": e_description,
                    "color": e_color,
                    "timestamp": str(datetime.utcnow().isoformat()),
                    "footer": {
                        "text": f"{BOT_NAME} v{__version__} on '{socket.gethostname()}'"
                    }
                }
            ]

        # add embed image, if applicable
        if 'embeds' in json and e_image:
            json['embeds'][0]['image'] = {
                "url": e_image
            }
        
        # return the dict
        return json