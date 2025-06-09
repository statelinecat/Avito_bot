from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from datetime import datetime, timedelta

def remove_from_delay_file(filename, url):
    try:
        with open(filename, 'r') as file:
            lines = file.read().splitlines()
        with open(filename, 'w') as file:
            for line in lines:
                if not line.startswith(f"{url}|"):
                    file.write(line + '\n')
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def write_to_file(filename, data):
    with open(filename, 'a') as file:
        file.write(data + '\n')

def write_to_delay_file(filename, url, timestamp, last_message=""):
    try:
    
        remove_from_delay_file(filename, url)
      
        with open(filename, 'a') as file:
            file.write(f"{url}|{timestamp}|{last_message}\n")
    except Exception as e:
        print(f"Ошибка при записи в {filename}: {e}")

def should_remove_from_delay(delay_entry, hours=24):
    url, timestamp, *rest = delay_entry.split('|')
    delay_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    time_difference = current_time - delay_time
    return time_difference > timedelta(hours=hours)

def remove_from_file(filename, data):
    try:
        with open(filename, 'r') as file:
            lines = file.read().splitlines()
        with open(filename, 'w') as file:
            for line in lines:
                if line.strip() != data.strip():
                    file.write(line + '\n')
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")

def get_last_message_text(driver):
    # получение послдених сообщений клиента
    try:
        last_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="message-item"]:last-child'))
        )
        return last_message.text
    except:
        return ""

def send_message(driver, message):
    # функция отправки сообщений
    try:
        message_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="chat/input"]'))
        )
        message_input.send_keys(message)
        driver.find_element(By.CSS_SELECTOR, 'button[data-marker="chat/send-button"]').click()
        time.sleep(random.randint(1, 3))
        return True
    except:
        return False

def get_wait_time(delay_entry):
    try:
        url, timestamp, *rest = delay_entry.split('|')
        delay_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        return (current_time - delay_time).total_seconds() / 3600
    except Exception as e:
        return None

def handle_dialog(driver, dialog, dialog_url, is_unread=False):
    # основная обработка всех диалогов
    try:
        dialog.click()
        time.sleep(random.randint(2, 4))

        last_message = get_last_message_text(driver)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if "риелтор" in last_message.lower():
            response = "Жаль, нам бы хотелось провести сделку лично с собственником"
            send_message(driver, response)
            write_to_delay_file("processed_dialogs.txt", dialog_url, current_time, "realtor")
            return True
        elif "не риелтор" in last_message.lower() or "частное лицо" in last_message.lower():
            response = "Жаль, нам бы хотелось провести сделку совместно с риелтором"
            send_message(driver, response)
            write_to_delay_file("processed_dialogs.txt", dialog_url, current_time, "private")
            return True
        elif is_unread:
            write_to_delay_file("processed_dialogs.txt", dialog_url, current_time, "unread")
            return False
        else:
            last_interaction = get_last_interaction_time(dialog_url)
            if last_interaction and (datetime.now() - last_interaction).total_seconds() > 10800:  # 3 часа
                send_message(driver, "Вы тут?")
                write_to_delay_file("processed_dialogs.txt", dialog_url, current_time, "reminder")
            return False
    except Exception as e:
        print(f"Ошибка при обработке диалога: {e}")
        return False

def check_unread_messages(driver):
    # проверка непрочитанных диалогов
    try:
        driver.get("https://www.avito.ru/chat")
        time.sleep(random.randint(3, 5))

        unread_dialogs = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-marker="chat-item"][class*="unread"]'))
        )

        for dialog in unread_dialogs:
            dialog_url = dialog.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            handle_dialog(driver, dialog, dialog_url, is_unread=True)
            time.sleep(random.randint(3, 7))

        processed_dialogs = load_processed_dialogs()
        for dialog_url, timestamp, status in processed_dialogs:
            if status in ["unread", "reminder"]:
                dialog_element = driver.find_element(By.CSS_SELECTOR, f'a[href="{dialog_url}"]')
                handle_dialog(driver, dialog_element, dialog_url)
                time.sleep(random.randint(3, 7))
    except Exception as e:
        print(f"Ошибка при проверке сообщений: {e}")