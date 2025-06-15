import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def check_unread_messages(driver):
    """Проверка сообщений с обработкой ошибок"""
    try:
        print("Открываем страницу сообщений...")
        driver.get("https://www.avito.ru/chat")
        time.sleep(random.uniform(3, 5))

        # Ожидаем загрузки чатов
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@data-marker, "chat-item")]'))
        )

        print("Проверка сообщений завершена")

    except Exception as e:
        print(f"Ошибка при проверке сообщений: {str(e)}")
        driver.save_screenshot("messages_error.png")