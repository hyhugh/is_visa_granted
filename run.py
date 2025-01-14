import time
import asyncio
import shutil

import numpy as np
import undetected_chromedriver as uc
from PIL import Image
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

        # Take a screenshot
        screenshot_path = "new_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved at: {screenshot_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()


def are_images_identical(image1_path, image2_path):
    try:
        # Open images
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        # Ensure the images have the same size
        if image1.size != image2.size:
            print("Images have different sizes.")
            return False

        # Convert images to numpy arrays
        image1_array = np.array(image1)
        image2_array = np.array(image2)

        # Compare pixel values
        return np.array_equal(image1_array, image2_array)
    except Exception as e:
        print(f"Error comparing images: {e}")
        return False


def send_image_via_telegram(bot_token, chat_id, image_path):
    try:
        bot = Bot(token=bot_token)
        asyncio.run(
            bot.send_photo(chat_id=chat_id, photo=open(image_path, "rb"))
        )
        print(f"Image sent successfully to chat ID {chat_id}.")
        return True
    except Exception as e:
        print(f"Error sending image: {e}")
        return False


def send_text_via_telegram(bot_token, chat_id, message):
    try:
        bot = Bot(token=bot_token)
        asyncio.run(bot.send_message(chat_id=chat_id, text=message))
        print(f"Image sent successfully to chat ID {chat_id}.")
        return True
    except Exception as e:
        print(f"Error sending image: {e}")
        return False


def telegram_notify(is_updated):
    if is_updated:
        send_image_via_telegram(
            TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "new_screenshot.png"
        )
    else:
        send_text_via_telegram(
            TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, "Not updated"
        )


def job():
    login_and_screenshot()
    is_updated = not are_images_identical(
        "old_screenshot.png", "new_screenshot.png"
    )
    telegram_notify(is_updated)
    shutil.copy("new_screenshot.png", "old_screenshot.png")


periodic = True

if __name__ == "__main__":
    if periodic:
        while True:
            job()
            time.sleep(15 * 60)
    else:
        job()
