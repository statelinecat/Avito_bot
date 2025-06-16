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
    """Заглушка для получения последнего сообщения клиента"""
    # TODO: Реализовать получение последнего сообщения
    print("Получение последнего сообщения (заглушка)")
    return ""
    # Пример реализации:
    # try:
    #     last_msg = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, "div.message-text:last-child"))
    #     return last_msg.text
    # except Exception:
    #     return ""

def send_message(driver, message):
    """Заглушка для отправки сообщений"""
    # TODO: Реализовать отправку сообщения
    print(f"Отправка сообщения: {message} (заглушка)")
    # Пример реализации:
    # try:
    #     input_field = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.message-input")))
    #     input_field.send_keys(message)
    #     send_btn = driver.find_element(By.CSS_SELECTOR, "button.send-button")
    #     send_btn.click()
    # except Exception as e:
    #     print(f"Ошибка при отправке сообщения: {e}")

def get_wait_time(delay_entry):
    try:
        url, timestamp, *rest = delay_entry.split('|')
        delay_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        return (current_time - delay_time).total_seconds() / 3600
    except Exception as e:
        return None

def handle_dialog(driver, dialog, dialog_url, is_unread=False):
    """Заглушка для обработки диалога"""
    # TODO: Реализовать обработку диалога
    print(f"Обработка диалога {dialog_url} (заглушка)")
    # Пример реализации:
    # 1. Проверить, нужно ли отвечать в этом диалоге
    # 2. Определить тип ответа (на риелтора/не риелтора)
    # 3. Отправить соответствующий ответ
    # 4. Записать в файл задержек

def check_unread_messages(driver):
    """Заглушка для проверки непрочитанных сообщений"""
    # TODO: Реализовать проверку непрочитанных сообщений
    print("Проверка непрочитанных сообщений (заглушка)")
    # Пример реализации:
    # 1. Открыть раздел сообщений
    # 2. Найти все непрочитанные диалоги
    # 3. Для каждого вызвать handle_dialog()
    # 4. Проверить диалоги из файла задержек