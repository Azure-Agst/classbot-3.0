import sys
import signal

from .utils import DiscordNotifier, env
from .scripts.fsu_enroll import FSU_Enroller
from .version import __version__, __author__, __email__

class Classbot:

    def __init__(self):
        """Initialize Classbot"""

        # Print Header
        print(f"\nClassbot-3.0 - {__version__}")
        print("\"Third time's the charm, am I right?\"")
        print(f"(c) 2022 {__author__} <{__email__}>")

        # Disclaimers
        print("\nThis program is intended for use by authorized users only. Unauthorized use")
        print("or redistribution of this program is strictly forbidden. This program is not")
        print("responsible for any damage caused by using this program. All rights reserved by")
        print("coypright holder. Smiles! :)\n")

        # Check for discord webhook in environment variables
        # NOTE: The only reason this is here rather than env.py is because
        #       I expect implementing other notifiers in the future, so i dont
        #       want to have to edit env if I add another notifier. whatever.
        if env.discord_url is None:
            print("ERROR: Environment variable 'DISCORD_URL' not set.")
            return

        # Init DiscordNotifier
        self.notifier = DiscordNotifier(env.discord_url)

        # Initialize our driver and start it up
        self.driver = self.init_driver()
        self.script = FSU_Enroller(self.driver, self.notifier)

        # Register signal handlers
        signal.signal(signal.SIGTERM, self.sigterm_handler)

        # Notify discord that we're starting
        self.notifier.send_embed(
            title="Classbot-3.0 is booting up!",
            description=f"Username: `{env.username}`\n" + \
                f"Driver: `{env.driver}`\n" + \
                f"Script: `{self.script.__class__.__name__}`",
            color=DiscordNotifier.Colors.INFO
        )

    def run(self):
        """Run Classbot"""

        # Run, save exit code, then exit
        exit_code = self.script.run()
        self.exit_handler(exit_code)

    def init_driver(self):
        """Initializes the driver, depending on env var"""

        if env.driver.lower() == "firefox":
            print("Using Firefox driver!")
            from .drivers.firefox import FirefoxDriver
            return FirefoxDriver().new_driver()

        elif env.driver.lower() == "browserless":
            print("Using Browserless driver!")
            from .drivers.browserless import BrowserlessDriver
            return BrowserlessDriver().new_driver()

        elif env.driver.lower() == "docker":
            print("Using Docker driver!")
            from .drivers.docker import DockerDriver
            return DockerDriver().new_driver()

        if env.driver is None:
            print("ERROR: Environment variable 'DRIVER' not set properly.")
            return
    
    def sigterm_handler(self):
        """Handle SIGTERM"""

        print("\nSIGTERM received, exiting...")

        self.driver.quit()
        self.notifier.send_embed(
            title="Terminated!",
            description="Classbot encountered a SIGTERM! " + \
                "Did you stop the docker image? " + \
                "Shutting down...",
            color=DiscordNotifier.Colors.DANGER
        )

        sys.exit(0)

    def exit_handler(self, exit_code: int = 0):
        """Handle exiting normally"""

        print("\nClassbot has shut down.")

        self.driver.quit()
        self.notifier.send_embed(
            title="Shutting down!",
            description="Classbot exited with status code: " + \
                f"`{exit_code}`!",
            color=DiscordNotifier.Colors.DANGER
        )

        sys.exit(exit_code)

if __name__ == "__main__":
    Classbot().run()
