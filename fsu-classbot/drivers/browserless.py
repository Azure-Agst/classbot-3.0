import requests

from ..utils import env

from selenium import webdriver

class BrowserlessDriver():
    """Creates a remote browserless driver, which uses Chrome"""

    def new_driver(self):
        """Creates a browserless-attached driver"""

        # check url was set
        if env.remote_url is None:
            raise Exception("Remote URL not set!")

        # make sure server url is in right format
        if not env.remote_url.startswith('http'):
            raise Exception("Remote URL must start with 'http' or 'https'!")

        # data manipulation
        protocol = env.remote_url.split('//')[0].replace(':', '')
        domain = env.remote_url.split('//')[1].split('/')[0]

        # make sure server url is contactable
        try:
            requests.get(
                f"{protocol}://{domain}/config",
                timeout=5
            )
        except Exception as e:
            raise Exception(f"Could not connect to remote server: {e}")
        print("Able to contact remote! Making session...")

        # set up options for driver
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")

        # create driver
        remote_url = f"{protocol}://{domain}/webdriver"
        print("Remote:" + remote_url)
        driver = webdriver.Remote(
            command_executor=remote_url,
            options=options
        )

        # return driver
        print("Session initiated!")
        return driver
    
