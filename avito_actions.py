from data_storage import load_ids, save_id, PRIVATE_SELLERS_FILE
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_items(driver):
    """Получаем список объявлений с улучшенной обработкой"""
    try:
        print("Загружаем страницу с объявлениями...")
        driver.get("https://www.avito.ru/kostroma/nedvizhimost")

        # Добавляем явные ожидания
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-marker="item"]'))
        )

        # Прокручиваем страницу для загрузки всех объявлений
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        items = driver.find_elements(By.XPATH, '//div[@data-marker="item"]')
        print(f"Найдено {len(items)} объявлений")
        return items

    except Exception as e:
        print(f"Ошибка при получении объявлений: {str(e)}")
        driver.save_screenshot("get_items_error.png")
        return []

def process_avito_pages(driver):
    """Основная функция обработки объявлений"""
    processed_count = 0
    max_ads_per_day = 20  # Лимит объявлений в день

    print("Начинаем обработку объявлений...")
    try:
        ads = get_items(driver)
        if not ads:
            print("Не найдено объявлений для обработки")
            return

        for ad in ads:
            try:
                ad_url = ad.get_attribute('href')
                if ad_url and ad_url not in load_ids(PRIVATE_SELLERS_FILE):
                    print(f"Обрабатываем объявление: {ad_url}")
                    # Здесь должна быть логика обработки объявления
                    save_id(PRIVATE_SELLERS_FILE, ad_url)
                    processed_count += 1
                    time.sleep(random.uniform(5, 10))

                    if processed_count >= max_ads_per_day:
                        break
            except Exception as e:
                print(f"Ошибка при обработке объявления: {str(e)}")
                continue

        print(f"Обработано {processed_count} объявлений за сегодня.")
    except Exception as e:
        print(f"Ошибка в основном цикле обработки: {str(e)}")