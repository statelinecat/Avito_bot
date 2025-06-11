import pickle
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

PHONE_NUMBER = "+79858037246"
PASSWORD = "al36avitodelis"


def run_avito_auth():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-webgl-swiftshader")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.avito.ru/#login?authsrc=h")
    time.sleep(random.randint(1, 2))

    current_url = driver.current_url
    if "login" not in current_url:
        print("Ошибка: Бот не находится на странице авторизации.")
        return

    # здесь пишите код для основной авторизации

    try:
        new_block = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="header/menu-profile"]'))
        )
        actions = ActionChains(driver)
        actions.move_to_element(new_block)
        actions.perform()

        profile_switch_second = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-marker="profile-switch/second"] span[role="button"]'))
        )
        print("Элемент profile-switch/second span[role='button'] найден, выполняю клик.")
        driver.execute_script("arguments[0].click();", profile_switch_second)
        
        actions.reset_actions()
        time.sleep(random.randint(10, 15))
    except Exception as e:
        print(f"Ошибка при выборе профиля: {e}")
        driver.quit()
        return None

    print("Авторизация успешно завершена!")
    save_cookies(driver)

    return driver