import os
from dotenv import load_dotenv

class EnvDict():
    """Class used for representing environment variables."""

    def __repr__(self):
        return f"{self.__class__.__name__}{self.__dict__}"

    def __init__(self):
        """Read in env vars"""
        
        # read in dotenv, if exists
        load_dotenv()

        # username
        self.username = os.getenv('FSU_USERNAME')
        if not self.username:
            raise Exception("FSU_USERNAME not set!")

        # password
        self.password = os.getenv('FSU_PASSWORD')
        if not self.password:
            raise Exception("FSU_PASSWORD not set!")

        # semester
        valid_semesters = ['fall', 'spring', 'summer']
        self.semester = str(os.getenv('FSU_SEMESTER')).lower()
        if self.semester not in valid_semesters:
            raise Exception("FSU_SEMESTER not set to valid option!")

        # discord stuff
        self.discord_url = os.getenv('DISCORD_URL')
        self.discord_pings = os.getenv('DISCORD_PINGS')
        self.discord_modulo = int(os.getenv('DISCORD_MODULO')) \
            if os.getenv('DISCORD_MODULO') is not None else 5

        # selenium stuff
        self.driver = os.getenv('DRIVER')
        self.headless = os.getenv('DRIVER_HEADLESS', 'False') \
            .lower() in ('true', '1', 't')
        self.remote_url = os.getenv('DRIVER_REMOTE')
        self.timeout = os.getenv('DRIVER_TIMEOUT') \
            if os.getenv('DRIVER_TIMEOUT') is not None else 15
        self.sleep_time = os.getenv('DRIVER_SLEEP') \
            if os.getenv('DRIVER_SLEEP') is not None else 2

env = EnvDict()