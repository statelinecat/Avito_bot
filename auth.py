import pickle
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

PHONE_NUMBER = "ak12@bk.ru"
PASSWORD = "Al36avitodelis"
COOKIES_FILE = "cookies.pkl"

def save_cookies(driver, path=COOKIES_FILE):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print("Cookies сохранены.")

def load_cookies(driver, path=COOKIES_FILE):
    if os.path.exists(path):
        with open(path, "rb") as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            if "expiry" in cookie:
                del cookie["expiry"]  # Удаляем, чтобы не было ошибок
            driver.add_cookie(cookie)
        print("Cookies загружены.")
        return True
    return False

def run_avito_auth():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.avito.ru/")
    time.sleep(2)

    # Если есть cookies — пробуем зайти без авторизации
    if load_cookies(driver):
        driver.get("https://www.avito.ru/")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="header/menu-profile"]'))
            )
            print("Успешный вход с использованием cookies.")
            return driver
        except:
            print("Cookies недействительны. Авторизация будет выполнена вручную.")

    try:
        # Нажимаем "Вход и регистрация"
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-marker="login-button"]'))
        )
        login_button.click()

        # Переключаемся на вход по email
        email_tab = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-marker="popup-tabs.switchToEmail"]'))
        )
        email_tab.click()

        # Вводим email
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, 'login'))
        )
        email_input.clear()
        email_input.send_keys(PHONE_NUMBER)

        continue_button = driver.find_element(By.CSS_SELECTOR, 'button[data-marker="login-form/continue"]')
        continue_button.click()

        # Вводим пароль
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, 'password'))
        )
        password_input.clear()
        password_input.send_keys(PASSWORD)

        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[data-marker="login-form/submit"]')
        submit_button.click()

        # Ожидаем вход
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="header/menu-profile"]'))
        )

        # Проверка капчи (если есть)
        if "captcha" in driver.page_source.lower():
            print("Обнаружена капча! Требуется ручной ввод.")
            time.sleep(60)  # Дайте себе время на ручной ввод

        print("Авторизация прошла успешно.")
        time.sleep(random.randint(2, 3))

    except Exception as e:
        print(f"Ошибка во время авторизации: {e}")
        driver.quit()
        return None

    # Выбор второго профиля
    try:
        new_block = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="header/menu-profile"]'))
        )
        actions = ActionChains(driver)
        actions.move_to_element(new_block).perform()

        profile_switch_second = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[data-marker="profile-switch/second"] span[role="button"]'))
        )
        print("Элемент второго профиля найден. Переключаемся...")
        driver.execute_script("arguments[0].click();", profile_switch_second)
        actions.reset_actions()
        time.sleep(random.randint(3, 5))

    except Exception as e:
        print(f"Ошибка при выборе профиля: {e}")
        driver.quit()
        return None

    save_cookies(driver)
    return driver
