from ..utils import env

from selenium import webdriver

class DockerDriver():
    """Creates a remote driver, which uses Firefox"""

    def new_driver(self):
        """Creates a selenium driver"""

        # set up options for driver
        options = webdriver.FirefoxOptions()
        if env.headless:
            options.add_argument("-headless")

        # ensure env var was set
        if env.remote_url is None:
            raise Exception("Remote URL not set!")

        # create driver
        return webdriver.Remote(
            command_executor=env.remote_url, 
            options=options
        )
    
