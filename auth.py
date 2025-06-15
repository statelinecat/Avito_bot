import pickle
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

PHONE_NUMBER = "ak12@bk.ru"
PASSWORD = "Al36avitodelis"


def save_cookies(driver):
    """Сохраняет куки после успешной авторизации"""
    pickle.dump(driver.get_cookies(), open("avito_cookies.pkl", "wb"))


def run_avito_auth():
    # Настройка браузера
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        # Инициализация драйвера
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Открываем страницу авторизации напрямую
        print("Открываем страницу авторизации...")
        driver.get("https://www.avito.ru/#login?authsrc=h")
        time.sleep(5)  # Даем время для загрузки

        # Ожидаем когда пользователь решит капчу вручную
        print("Пожалуйста, решите капчу в открывшемся браузере...")
        input("После успешного решения капчи нажмите Enter в консоли для продолжения...")

        # После решения капчи перезагружаем страницу
        driver.refresh()
        time.sleep(3)

        # Теперь пробуем авторизоваться
        print("Пытаемся войти в аккаунт...")

        # Вводим email
        try:
            email_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@name="login" or contains(@data-marker, "login-form/login")]'))
            )
            email_input.clear()
            for char in PHONE_NUMBER:
                email_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
        except Exception as e:
            print(f"Ошибка при вводе email: {str(e)}")
            driver.save_screenshot("email_error.png")
            return None

        # Вводим пароль
        try:
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@name="password" or contains(@data-marker, "login-form/password")]'))
            )
            password_input.clear()
            for char in PASSWORD:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
        except Exception as e:
            print(f"Ошибка при вводе пароля: {str(e)}")
            driver.save_screenshot("password_error.png")
            return None

        # Кликаем кнопку входа
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(., "Войти") or contains(@data-marker, "login-form/submit")]'))
            )
            submit_button.click()
            time.sleep(5)
        except Exception as e:
            print(f"Ошибка при нажатии кнопки входа: {str(e)}")
            driver.save_screenshot("submit_error.png")
            return None

        # Проверяем успешность авторизации
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@data-marker, "header/menu-profile")]'))
            )
            print("Авторизация успешна!")
            save_cookies(driver)
            return driver
        except Exception as e:
            print(f"Не удалось подтвердить авторизацию: {str(e)}")
            driver.save_screenshot("auth_failed.png")
            return None

    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        if 'driver' in locals():
            driver.save_screenshot("critical_error.png")
            driver.quit()
        return None