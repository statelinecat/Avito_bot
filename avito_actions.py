from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import datetime
from data_storage import load_ids, save_id
from messenger_handler import write_to_delay_file

MESSAGE_VARIANTS = [
    [
        "Здравствуйте!",
        "Понравилось ваше объявление!",
        "Еще продаете?",
        "Скажите, вы риелтор?"
    ],
    [
        "Добрый день!",
        "Отличное объявление",
        "Еще актуально?",
        "Вы случаем не риелтор?"
    ]
]


def is_private_seller(driver):
    try:
        seller_info = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="seller-info/label"]')))
        return "Частное лицо" in seller_info.text
    except:
        return False


def send_message_to_ad(driver, ad_url):
    try:
        driver.get(ad_url)
        time.sleep(random.randint(2, 4))

        if not is_private_seller(driver):
            return False

        chat_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-marker="item-phone-button/button"]')))
        chat_button.click()
        time.sleep(random.randint(1, 2))

        message_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="chat/input"]')))

        message_variant = random.choice(MESSAGE_VARIANTS)
        for msg in message_variant:
            message_input.send_keys(msg)
            time.sleep(random.uniform(0.5, 1.5))
            driver.find_element(By.CSS_SELECTOR, 'button[data-marker="chat/send-button"]').click()
            time.sleep(random.randint(1, 2))

        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")
        return False


def process_avito_pages(driver):
    processed_count = 0
    max_ads_per_day = 20

    while processed_count < max_ads_per_day:
        try:
            ads = get_items(driver)
            if not ads:
                break

            for ad in ads:
                ad_url = ad.get_attribute('href')
                if ad_url and ad_url not in load_ids(PRIVATE_SELLERS_FILE):
                    if send_message_to_ad(driver, ad_url):
                        save_id(PRIVATE_SELLERS_FILE, ad_url)
                        processed_count += 1
                        time.sleep(random.randint(5, 10))

                        if processed_count >= max_ads_per_day:
                            break
        except Exception as e:
            print(f"Ошибка при обработке объявлений: {e}")
            time.sleep(10)

    print(f"Обработано {processed_count} объявлений за сегодня.")


def get_items(driver):
    try:
        driver.get("https://www.avito.ru/ваш_город/nekretnina")
        time.sleep(random.randint(3, 5))

        items = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-marker="item-title"]')))
        return items
    except Exception as e:
        print(f"Ошибка при получении объявлений: {e}")
        return []