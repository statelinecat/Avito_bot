# auth.py
import pickle
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

PHONE_NUMBER = "ak12@bk.ru"
PASSWORD = "Al36avitodelis"  # Убедитесь, что пароль правильный


def human_type(element, text, speed=(0.1, 0.3)):
    """Имитация человеческого ввода"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*speed))


def save_cookies(driver):
    """Сохраняет cookies сессии"""
    with open("avito_cookies_pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)


def load_cookies(driver):
    """Загружает cookies сессии"""
    try:
        with open("avito_cookies_pkl", "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
            return True
    except:
        return False


def run_avito_auth():
    # Настройка браузера
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Инициализация драйвера
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # 1. Попытка входа через cookies
        driver.get("https://www.avito.ru/")
        time.sleep(random.uniform(2, 4))

        if load_cookies(driver):
            driver.refresh()
            time.sleep(random.uniform(3, 5))

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="header/menu-profile"]'))
                )
                print("Успешная авторизация через cookies")
                return driver
            except:
                print("Cookies устарели, требуется повторная авторизация")

        # 2. Полная авторизация
        driver.get("https://www.avito.ru/#login?authsrc=h")
        time.sleep(random.uniform(3, 5))

        # Ввод email
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-marker="login-form/login"]'))
        )
        human_type(email_input, PHONE_NUMBER)
        time.sleep(random.uniform(0.5, 1.5))

        # Нажатие кнопки "Продолжить"
        continue_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-marker="login-form/submit"]'))
        )
        continue_btn.click()
        time.sleep(random.uniform(2, 3))

        # Ввод пароля
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-marker="login-form/password"]'))
        )
        human_type(password_input, PASSWORD)
        time.sleep(random.uniform(0.5, 1.5))

        # Нажатие кнопки "Войти"
        login_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-marker="login-form/submit"]'))
        )
        login_btn.click()

        # Ожидание успешной авторизации
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-marker="header/menu-profile"]'))
            )
            print("Авторизация успешно завершена!")
            save_cookies(driver)
            return driver
        except Exception as e:
            print(f"Не удалось подтвердить авторизацию: {e}")
            # Проверка на капчу
            if "captcha" in driver.page_source.lower():
                print("Обнаружена CAPTCHA! Требуется ручной ввод")
            driver.save_screenshot("auth_error.png")
            raise

    except Exception as e:
        print(f"Критическая ошибка при авторизации: {str(e)}")
        driver.save_screenshot("auth_error.png")
        if 'driver' in locals():
            driver.quit()
        return None