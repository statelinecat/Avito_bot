import json
import time
import random
from playwright.sync_api import sync_playwright

# === Настройки ===
USERNAME = "your_email@example.com"  # Не используется, если используешь cookies
PASSWORD = "your_password"            # Не используется, если используешь cookies
CITY = "kostroma"                     # Город для поиска недвижимости
MAX_MESSAGES = 20                     # Максимум сообщений в день


# === Функция восстановления сессии через cookies ===
def login_avito(page, context):
    print("Восстанавливаем сессию через cookies...")
    try:
        with open("avito_cookies.json", "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        page.goto("https://www.avito.ru/profile")
        time.sleep(3)

        if "profile" in page.url or "Профиль" in page.title():
            print("✅ Авторизация успешна через cookies")
        else:
            print("❌ Не удалось восстановить сессию")
    except Exception as e:
        print("❌ Ошибка при восстановлении сессии:", e)


# === Получение объявлений от частных лиц ===
def get_private_ads(page):
    print(f"Получаем объявления от частных лиц в городе {CITY}...")
    url = f"https://www.avito.ru/{CITY}/kvartiry/prodam?user_type=private"

    try:
        page.goto(url)
        time.sleep(3)

        # Сохраним HTML для диагностики
        html = page.content()
        with open("avito_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Сделаем скриншот
        page.screenshot(path="avito_page.png")

        # Проверим, есть ли текст блокировки
        if "Действие заблокировано" in html or "подозрительная активность" in html:
            print("❌ Доступ к странице заблокирован Avito")
            return []

        # Ждём появления объявлений
        try:
            page.wait_for_selector("a.link-link-39EVK", timeout=20000)
        except Exception:
            print("❌ Не найдено объявлений на странице")
            return []

        # Прокрутка страницы
        for i in range(5):
            print(f"👉 Прокрутка {i+1} из 5...")
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            time.sleep(random.uniform(2, 4))

        # Получаем ссылки
        ad_links = page.evaluate("""
            Array.from(document.querySelectorAll('a.link-link-39EVK')).map(link => link.href)
        """)
        full_links = [link for link in ad_links if "/prodam-" in link]
        print(f"✅ Найдено {len(full_links)} объявлений от частных лиц")
        return full_links

    except Exception as e:
        print("❌ Ошибка при загрузке страницы:", e)
        return []


# === Отправка сообщения по варианту 1 ===
def send_message_variant_1(page, ad_url):
    print(f"📩 Отправляем сообщение по объявлению: {ad_url}")
    page.goto(ad_url + "/contact")
    time.sleep(3)

    messages = [
        "Здравствуйте!",
        "Понравилось ваше объявление!",
        "Еще продаете?",
        "Скажите, вы риелтор?"
    ]

    message_box = page.locator("#message-textarea")

    for msg in messages:
        try:
            message_box.fill(msg)
            page.click("button[form='message-form']")
            print(f"📨 Отправлено: {msg}")
            time.sleep(random.uniform(1.5, 3))
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения: {e}")
            break

    print("✅ Сообщение полностью отправлено\n")


# === Основная функция запуска бота ===
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        login_avito(page, context)

        ads = get_private_ads(page)
        sent_count = 0

        for ad in ads:
            if sent_count >= MAX_MESSAGES:
                print("⚠️ Достигнут лимит в 20 сообщений за день.")
                break
            try:
                send_message_variant_1(page, ad)
                sent_count += 1
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"❌ Ошибка при работе с объявлением {ad}: {e}")

        print(f"✅ Сегодня отправлено: {sent_count} сообщений")

        context.close()
        browser.close()


# === Запуск скрипта ===
if __name__ == "__main__":
    main()