import time
import asyncio
import pytz
from datetime import datetime


import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from telegram import Bot

# Replace with your login credentials
USERNAME = ""
PASSWORD = ""
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""


def login_and_screenshot():
    driver = uc.Chrome(headless=False, use_subprocess=False)
    try:
        # Open the login page
        driver.get("https://online.immi.gov.au/lusc/login")
        print("Page opened.")

        # Wait for the login fields to load
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        # Enter credentials
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)

        # Submit the form
        password_field.send_keys(Keys.RETURN)
        print("Login form submitted.")

        # Click the "Continue" button
        continue_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Continue']")
            )
        )
        continue_button.click()
        print("Clicked the 'Continue' button.")

        # Wait for the page to load after login
        wait.until(
            EC.presence_of_element_located((By.ID, "MyAppsResultTab_0_0"))
        )
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "wc-datefield"))
        )

        div_content = driver.find_element(
            By.XPATH, '//*[@id="MyAppsResultTab_0_0-body"]/div/p/strong'
        ).text
        print(div_content)

        send_text_via_telegram(
            TELEGRAM_BOT_TOKEN,
            TELEGRAM_CHAT_ID,
            f"Latest status: {div_content}",
        )

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()


def send_text_via_telegram(bot_token, chat_id, message):
    try:
        bot = Bot(token=bot_token)
        asyncio.run(bot.send_message(chat_id=chat_id, text=message))
        print(f"Image sent successfully to chat ID {chat_id}.")
        return True
    except Exception as e:
        print(f"Error sending image: {e}")
        return False


def job():
    login_and_screenshot()


def is_night_in_sydney():
    # Define Sydney timezone
    sydney_tz = pytz.timezone("Australia/Sydney")

    # Get current time in Sydney
    now_in_sydney = datetime.now(sydney_tz)

    # Define daytime hours (6 AM to 6 PM)
    sunrise_hour = 7
    sunset_hour = 18

    # Check if the current time is outside daytime hours
    return (
        now_in_sydney.hour < sunrise_hour or now_in_sydney.hour >= sunset_hour
    )


periodic = True

if __name__ == "__main__":
    if periodic:
        while True:
            if is_night_in_sydney():
                print("It's night in Sydney. Waiting for daytime...")
                time.sleep(15 * 60)
                continue
            try:
                job()
                time.sleep(15 * 60)
            except:
                pass
    else:
        job()
