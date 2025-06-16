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

def send_message(driver, message):
    # функция отправки сообщений

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

def check_unread_messages(driver):
    # проверка непрочитанных диалогов