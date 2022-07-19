import shutil

from ..utils import env

from selenium import webdriver

class FirefoxDriver():
    """Creates a selenium driver which uses Firefox"""

    def new_driver(self):
        """Creates a selenium driver"""

        # make sure geckodriver is in path
        gd_path = shutil.which('geckodriver')
        if not gd_path:
            raise Exception("Geckodriver not found in path!")

        # set up options for driver
        options = webdriver.FirefoxOptions()
        if env.headless:
            options.add_argument("-headless")

        # create driver
        return webdriver.Firefox(
            executable_path=gd_path, 
            options=options
        )
    
