from .utils import DiscordNotifier, env
from .scripts.fsu_enroll import EnrollMe

def main():

    # Start
    print("#########################################")
    print("#            fsu_classbot.py            #")
    print("#  Third time's the charm, am I right?  #")
    print("#     Copyright (c) 2022 Azure-Agst     #")
    print("#########################################")

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

    # Initialize our driver
    if env.driver.lower() == "firefox":
        print("Using Firefox driver!")
        from .drivers.firefox import FirefoxDriver
        driver = FirefoxDriver().new_driver()

    elif env.driver.lower() == "browserless":
        print("Using Browserless driver!")
        from .drivers.browserless import BrowserlessDriver
        driver = BrowserlessDriver().new_driver()

    if env.driver is None:
        print("ERROR: Environment variable 'DRIVER' not set.")
        return

    # Go ahead and start it up
    script = EnrollMe(driver, discord)

    # Notify discord that we've started
    discord.send_embed(
        title="Starting up!",
        message="Classbot is booting up...\n" + \
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
        message="Classbot is shutting down...",
        color=DiscordNotifier.Colors.DANGER
    )
    print("\nClassbot has shut down.")
    return 0


if __name__ == "__main__":
    exit(main())