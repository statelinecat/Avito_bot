import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import EMAIL, PASSWORD

COOKIES_FILE = "cookies.json"

def save_cookies_from_driver(driver):
    cookies = driver.get_cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)

def load_cookies():
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            return json.load(f)
    return None

def update_cookies():
    options = Options()
    # 🟡 Убираем headless для отладки
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.avito.ru/#login?authsrc=h")

    try:
        print("Ждём кнопку входа...")
        login_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-marker="login-button"]'))
        )
        login_btn.click()
        print("Клик по кнопке входа выполнен.")

        print("Переход на вкладку Email...")
        email_tab = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-marker="popup-tabs.switchToEmail"]'))
        )
        email_tab.click()

        print("Вводим логин...")
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'login')))
        email_input.send_keys(EMAIL)

        driver.find_element(By.CSS_SELECTOR, 'button[data-marker="login-form/continue"]').click()

        print("Вводим пароль...")
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
        password_input.send_keys(PASSWORD)

        driver.find_element(By.CSS_SELECTOR, 'button[data-marker="login-form/submit"]').click()

        print("Ожидаем вход...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="header/menu-profile"]'))
        )

        save_cookies_from_driver(driver)
        print("Cookies обновлены.")
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
    finally:
        driver.quit()

