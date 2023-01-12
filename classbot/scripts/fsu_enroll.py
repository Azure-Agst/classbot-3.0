import time
import json
import traceback
from os import path
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..utils import DiscordNotifier, env
from ..utils.drivertools import check_xpath_exists, get_wait
from ..utils.cookies import load_cookies, save_cookies

class FSU_Enroller():
    """Main script for handling enrolling"""

    def __init__(self, driver, discord) -> None:
        """Initialize EnrollMe"""

        # save vars from parent scope
        self.driver = driver
        self.discord = discord

    def run(self) -> None:
        """Run the enroll script"""

        # Do everything in a giant try/except block
        try:

            # Load cookies, if available.
            load_cookies(self.driver)

            # 1.) Login
            print("Attempting login...")
            login_status = self.login()

            # 1.1) Check for bad password
            if login_status == 1:
                print("Bad password")
                self.discord.send_embed(
                    title="Bad Password!",
                    description="Your password is incorrect! Please check your credentials and relaunch.",
                    color=DiscordNotifier.Colors.DANGER
                )
                return

            # 1.2) Check for 2fa
            elif login_status == 2:
                self.handle_duo()

            # 2) Navigate to Start
            print("Navigating to Start...")
            self.nav_to_start()

            # 3) Enroll
            print("Starting main enrollment loop...")
            return self.main_enrollment_loop()

        #
        # Now we catch every exception we can!
        #

        # In case we trigger a timeout
        except TimeoutException:
            print("\nEC Timeout Encountered! Exiting...")
            tb = traceback.format_exc()
            self.discord.send_embed(
                title="Expected Condition Timeout Encountered!",
                description="This occurs whenever an Expected Condition " + \
                    "is unable to resolve within the set timeout. Sometimes " + \
                    "this is because the servers are under load, and sometimes " + \
                    "its due to elements missing entirely! Try increasing  " + \
                    "`DRIVER_TIMEOUT` or running the bot locally to debug!" + \
                    (f"\n\n```\n{tb}\n```" if env.debug else ""),
                color=DiscordNotifier.Colors.DANGER
            )
            return -1

        # In case we get interrupted by a keyboard interrupt
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt Encountered! Exiting...")
            self.discord.send_embed(
                title="Keyboard Interrupt Encountered!",
                description="You have interrupted the program!",
                color=DiscordNotifier.Colors.DANGER
            )
            return -2
        
        # In case our connection to our browser gets refused
        # This happens if the user takes control of the browser
        except ConnectionRefusedError:
            print("\nConnection Refused Exception Encountered! Exiting...")
            self.discord.send_embed(
                title="Connection Refused Encountered!",
                description="The connection to the browser was refused! Maybe the browser is down?",
                color=DiscordNotifier.Colors.DANGER
            )
            return -3
        
        # In case the browser window is closed
        except WebDriverException as e:
            print("\nGeneric WebDriver Exception Encountered! Exiting...")
            print(str(e))
            print(traceback.format_exc())            
            self.discord.send_embed(
                title="WebDriver Exception Encountered!",
                description="The browser window was closed! Maybe this was expected? Check the logs!",
                color=DiscordNotifier.Colors.DANGER
            )
            return -4

        # Catch all, in case we encounter unexpected crashes
        except Exception as e:
            print(f"\nUnknown Exception Encountered! Exiting...\n{e}")
            self.discord.send_embed(
                title="Unknown Exception Encountered!",
                description="An unknown exception has occurred! " + \
                    "Please check the logs for more details.\n\n" + \
                    f"`{type(e).__name__}: {str(e)}`",
                color=DiscordNotifier.Colors.DANGER
            )
            return -5


    def login(self) -> int:
        """
        Step 1.) Login to FSU
        - This function handles logging into the account
        """

        # Navigate to url
        self.driver.get("http://www.my.fsu.edu")

        # Type in username and password
        self.driver.find_element(By.ID, 'username').send_keys(env.username)
        self.driver.find_element(By.ID, 'password').send_keys(env.password)

        # Press enter to submit
        self.driver.find_element(By.ID, 'fsu-login-button').click()

        # Sleep a few seconds to let stuff load
        time.sleep(2)

        # Check to see if bad password error exists
        if check_xpath_exists(self.driver, '//*[@id="msg"]'):
            return 1

        # Check to see if 2fa modal is visible
        if check_xpath_exists(self.driver, '//*[@id="duo_iframe"]'):
            return 2

        # Else, logged in!
        return 0

    
    def handle_duo(self) -> int:
        """
        Step 1.2.) Handle Duo
        - Handles waiting for user to activate 2FA
        """

        # Print statement
        print(f"Duo detected! ", end="", flush=True)

        # Swap to Duo iFrame
        get_wait(self.driver).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, '//*[@id="duo_iframe"]')
            )
        )

        # Sleep to let everything load.
        # NOTE: Can't do a wait condition here bc the frame looks totally
        #       different when "Remember Me" cookies skip 2FA entirely.
        time.sleep(1)

        # See if we have to deal with interaction here
        if check_xpath_exists(self.driver, '//*[@id="auth_methods"]'):

            # Get the API endpoint for our iframe
            duo_api_url = urlparse(self.driver.current_url).netloc

            # Send discord message letting people know approval is required
            duo_msg = self.discord.send_embed(
                title="Duo Approval Required!",
                description="Please accept 2FA on your device to continue.\n" + \
                    "If this is your first time approving, you may need to approve twice.",
                color=DiscordNotifier.Colors.WARNING
            )

            # See if auto-login message exists. If it does, auto-login started.
            # Cancel auto login, ask to remember, then re-auth.
            if check_xpath_exists(self.driver, '//*[@class="message-text"]'):               

                # Click Cancel
                get_wait(self.driver).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@class="btn-cancel"]')
                    )
                ).click()

                # Click Remember Me
                get_wait(self.driver).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@name="dampen_choice"]')
                    )
                ).click()

                # Click the user's default method button
                get_wait(self.driver).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@class="used-automatically"]/../../button')
                    )
                ).click()

            # Print that we're now waiting
            print("Awaiting user input...", end="", flush=True)

            # Enter endless loop, where we're checking the status message
            while True:

                # Get message element, or nothing if closed
                if check_xpath_exists(self.driver, '//*[@class="message-text"]'):
                    message = self.driver.find_element(By.XPATH, '//*[@class="message-text"]').text
                else:
                    message = ""

                # If success in message, we're good!
                if "success" in message.lower():

                    # End bullet point line
                    print("\nDuo no longer detected! Proceeding!")

                    # Save our cookies
                    save_cookies(duo_api_url, self.driver)

                    # Update Discord Message
                    self.discord.update_embed(
                        duo_msg,
                        title="Duo Approved!",
                        description="The script is now proceeding!",
                        color=DiscordNotifier.Colors.SUCCESS
                    )

                    # Done here
                    break

        # If we get the "Logging you in..." page, we can skip!
        else:
            print("Handled via auth caching!")

        # Swap back to default content
        self.driver.switch_to.default_content()

        # Wait for title to change, meaning new page is loaded
        get_wait(self.driver).until(
            EC.title_contains("myFSU Portal")
        )

        # return success
        return 0


    def nav_to_start(self):
        """
        Step 2.) Navigate to Start
        - Navigate driver through website to get to loop starting point
        """

        # Click on Student Central icon in the "myFSU Links" section
        # Sometimes the home page doesn't like loading and needs a refresh.
        # Wait a few seconds and see if the SC icon has loaded.
        # If it hasn't, we need a refresh.
        while True:
            try:
                if "Homepage" not in self.driver.title:
                    e = get_wait(self.driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[@title='Student Central']")
                        )
                    ).click()
                else:
                    break
            except TimeoutException:
                print("Home page failed to load! Refreshing...")
                self.driver.refresh()
                time.sleep(3)

        # Determine whether or not we're in Student version of SC
        # If not, run JS to swap to student tab
        current_tab = self.driver.find_element(By.XPATH, '//*[@id="HOMEPAGE_SELECTOR$PIMG"]/span').text
        current_tab_clean = current_tab.split("<br>")[-1].split("\n")[0].lower()
        if "student" not in current_tab_clean:

            # Javascript that swaps the pages
            self.driver.execute_script('lpSwipeToTabFromDD("SA.EMPLOYEE.FSU_STUDENT_HP");')

            # Sleep a sec
            time.sleep(2)

        # Click on "My Classes"
        get_wait(self.driver).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="win0divPTNUI_LAND_REC_GROUPLET$10"]')
            )
        ).click()

        # Sleep 2 seconds
        time.sleep(2)
        
        # Clicking won't work, so run some really bastardized
        # JavaScript to swap to the Add Classes tab.
        self.driver.execute_script("""
            top.ptgpPage.openUrlWithWarning(
                'https://campusadmin.omni.fsu.edu/psc/sprdcs_newwin/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_CART.GBL?NavColl=true', 
                'top.ptgpPage.selectStep(\\'ADMN_S201807141525557333111812\\');', 
                false
            );
        """)

        # The actual enrollment process operates within an iframe, 
        # so we need to swap to it
        get_wait(self.driver).until(
            EC.frame_to_be_available_and_switch_to_it(
                (By.XPATH, '//*[@id="main_target_win0"]')
            )
        )

        # See if semester table exists
        # If so, we need to select the right semester
        if check_xpath_exists(self.driver, '//*[@id="PSLEVEL2GRID"]'):

            # Wait for semester table to render, then enumerate it and pick the
            # option that corresponds to the requested semester
            semesters = get_wait(self.driver).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, 'PSLEVEL2GRID')
                )
            ).find_elements(
                By.CSS_SELECTOR, "span[id*='TERM_CAR$']"
            )

            # Loop through semesters and find the one we want
            idx = -1
            for i, semester in enumerate(semesters):
                if env.semester in semester.text.lower():
                    print(f"Found semester: {semester.text}! (Index: {i})")
                    idx = i
                    break
            if idx == -1:
                raise Exception(f"Could not find semester: {env.semester}!")
            
            # Click on the semester
            get_wait(self.driver).until(
                EC.element_to_be_clickable(
                    (By.ID, f"win0divSSR_DUMMY_RECV1$sels${idx}$$0")
                )
            ).click()

            # Press "Continue" on term select screen
            get_wait(self.driver).until(
                EC.element_to_be_clickable(
                    (By.ID, 'DERIVED_SSS_SCT_SSR_PB_GO')
                )
            ).click()

        # We are now on the "Add Classes Screen!"
        return 0

    def main_enrollment_loop(self):
        """
        Step 3.) Main Enrollment Loop
        - This loop handles the main enrollment process
        """

        # Variable declarations
        loop_count = 0

        # Send discord message to let user know we've begun the loop
        start_msg = self.discord.send_embed(
            title="Enrollment Loop Started!",
            description=f"Loop count: `{loop_count}`",
            color=DiscordNotifier.Colors.LIGHT
        )

        # By this point, we should be on the cart screen...
        while True:

            # Set up a few vars to be used within our try/except block
            results = {}

            # Do everything within a try to catch exceptions
            try:

                # Get shopping cart table
                # NOTE: Now THIS is some functional programming!
                cart_rows = get_wait(self.driver).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="SSR_REGFORM_VW$scroll$0"]/tbody') # Class table body
                    )
                ).find_elements(
                    By.CSS_SELECTOR, "tr" # Here are our entries!
                )

                # Make sure we actually have classes to enroll into
                # There are always at least 2 rows in the table:
                # - If empty cart, first TR is the empty header row, second empty cart message row
                # - If cart has classes, first TR is the header row, second is the first class
                # First see if the table format has changed for whatever reason
                if len(cart_rows) < 2:
                    raise EmptyCartException("Less than two rows? Something went wrong!")

                # NOTE: Don't like this comparison because it's hardcoded, but
                # at the same time, using `in` seems so expensive, so whatever...
                elif cart_rows[1].text == "Your enrollment shopping cart is empty.":
                    raise EmptyCartException("Your shopping cart is empty!")
                
                # If classes exist, lets try enrolling!
                # Click "Continue"
                get_wait(self.driver).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="gh-footer"]/ul/li/a')
                    )
                ).click()

                # Now we should be on the confirmation screen
                # Click "Finish Enrolling"
                get_wait(self.driver).until(
                    EC.element_to_be_clickable(
                       (By.XPATH, '//*[@id="gh-footer"]/ul/li[3]/a')
                    )
                ).click()

                # Now we should be on the results screen, get the results table
                # NOTE: The new UI uses bootstrap to make things look nicer, but
                #       the original table is still there, just hidden! Thanks
                #       sysadmins. :)
                results_table = get_wait(self.driver).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="SSR_SS_ERD_ER$scroll$0"]//table/tbody')
                    )
                ).find_elements(
                    By.CSS_SELECTOR, "tr"
                )
                
                # Loop through results table and check for errors
                for row in results_table:

                    # Get the cells of the row
                    cells = row.find_elements(
                        By.CSS_SELECTOR, "td"
                    )

                    # Extract data from cells
                    course_code = cells[0].find_element(By.CSS_SELECTOR, "span").text
                    raw_message = cells[1].find_element(By.XPATH, ".//div/div").text
                    clean_msg = raw_message.split("</b>")[-1].split("\n")[0]

                    # Append result to dictionary
                    results[course_code.replace(" ", "")] = {
                        "enrolled": "Success" in raw_message,
                        "message": clean_msg
                    }

                # Click "Add another class" and start over
                get_wait(self.driver).until(
                    EC.element_to_be_clickable(
                       (By.XPATH, '//*[@id="gh-footer"]/ul/li[2]/a')
                    )
                ).click()
            
            # In case we trigger a "Empty Cart" exception
            except EmptyCartException as e:
                print("\nEmpty Cart Exception Encountered! Exiting...")
                self.discord.delete_message(start_msg)
                self.discord.send_embed(
                    title="Empty Cart Exception Encountered!",
                    description=str(e), # cast to string to get text
                    color=DiscordNotifier.Colors.DANGER
                )
                return -6

            # Increment loop count
            loop_count += 1

            # Print loop count
            print(f"\rLoop Counter: {loop_count}", end="", flush=True)

            # Update webhook if modulo env var
            if loop_count % env.discord_modulo == 0:
                self.discord.update_embed(
                    start_msg,
                    description=f"Loop count: `{loop_count}`",
                )

            # Now, send an update message to discord if applicable:
            # - If any of our results were successes, send message
            # - If ALL of our results were successes, send message and exit
            res_bools = [result["enrolled"] for result in results.values()]
            if any(res_bools):

                # if all, set title; else if some, set title
                if all(res_bools):
                    title = "Successfully Enrolled in All Remaining Classes!"
                else:
                    title = "Successfully Enrolled in Some Classes..."

                # start message
                message = "You're now enrolled in the following classes:"

                # iterate over successful results
                print(f"\nSuccessfully enrolled into the following courses:")
                for course_code, result in results.items():
                    if result["enrolled"]:
                        print("\t" + course_code)
                        message += f"\n - `{course_code}`"

                # send embed
                self.discord.send_embed(
                    title=title,
                    description=message,
                    color=DiscordNotifier.Colors.SUCCESS
                )
            
                # if all: done here, so exit
                if all(res_bools):
                    return 0

            # We sleep and go again!
            time.sleep(env.sleep_time)

class EmptyCartException(Exception):
    pass
