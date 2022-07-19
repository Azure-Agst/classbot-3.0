from .utils import DiscordNotifier, env
from .scripts.fsu_enroll import FSU_Enroller
from .version import __version__, __author__, __email__

def main():

    # Print Header
    print(f"\nClassbot-3.0 - {__version__}")
    print("\"Third time's the charm, am I right?\"")
    print(f"(c) 2022 {__author__} <{__email__}>")

    # Disclaimers
    print("\nThis program is intended for use by authorized users only. Unauthorized use or")
    print("redistribution of this program is strictly forbidden. This program is not")
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
    discord = DiscordNotifier(env.discord_url)

    # Initialize our driver and start it up
    driver = init_driver()
    script = FSU_Enroller(driver, discord)

    # Notify discord that we've started
    discord.send_embed(
        title="Classbot is booting up!",
        description=f"Username: `{env.username}`\n" + \
            f"Driver: `{env.driver}`\n" + \
            f"Script: `{script.__class__.__name__}`",
        color=DiscordNotifier.Colors.INFO
    )

    # Run the script
    script.run()

    # Clean up
    driver.quit()
    discord.send_embed(
        title="Shutting down!",
        description="Classbot is shutting down...",
        color=DiscordNotifier.Colors.DANGER
    )
    print("\nClassbot has shut down.")
    return 0

def init_driver():
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

if __name__ == "__main__":
    exit(main())