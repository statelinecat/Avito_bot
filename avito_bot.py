import json
import time
import random
from playwright.sync_api import sync_playwright

# === Настройки ===
USERNAME = "ak12@bk.ru"  # Не используется, если используешь cookies
PASSWORD = "Al36avito"           # Не используется, если используешь cookies
CITY = "kostroma"                    # Город для поиска недвижимости
MAX_MESSAGES = 20                    # Максимум сообщений в день
HEADLESS = False                     # True - без открытия окна браузера


# === Функция восстановления сессии через cookies или вход ===
def login_avito(page):
    print("Проверяем наличие cookies...")
    try:
        with open("avito_state.json", "r"):
            pass
        print("Загружаем сохранённую сессию...")
        context = page.context()
        context.storage_state(path="avito_state.json")
        page.goto("https://www.avito.ru/profile")
        time.sleep(3)

        if "profile" in page.url or "Профиль" in page.title():
            print("✅ Авторизация успешна через cookies")
            return True
    except FileNotFoundError:
        print("❌ Cookies не найдены. Вход будет выполнен вручную.")

    print("Выполняем вход вручную... Зайдите в аккаунт.")
    page.goto("https://www.avito.ru/profile")
    input("👉 Нажмите Enter после входа в аккаунт...")

    # Сохраняем сессию после входа
    context = page.context()
    context.storage_state(path="avito_state.json")
    print("✅ Сессия сохранена")
    return True


# === Получение объявлений от частных лиц ===
def get_private_ads(page):
    print(f"🔍 Ищем объявления от частных лиц в городе {CITY}...")
    url = f"https://www.avito.ru/{CITY}/kvartiry/prodam?user_type=private"

    try:
        page.goto(url)
        time.sleep(random.uniform(5, 8))

        html = page.content()
        with open("avito_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        if "Действие заблокировано" in html or "подозрительная активность" in html:
            print("❌ Доступ к странице заблокирован Avito")
            return []

        print("⏳ Ждём загрузку объявлений...")
        page.wait_for_selector("a[itemprop='url']", timeout=15000)

        # Прокрутка страницы
        for i in range(5):
            print(f"👉 Прокрутка {i+1} из 5...")
            page.evaluate("window.scrollBy(0, 800)")
            time.sleep(random.uniform(3, 6))

        # Получаем уникальные ссылки
        links = page.locator("a[itemprop='url']").all_attribute_values("href")
        full_links = list(set(["https://www.avito.ru"  + link for link in links if "/prodam-" in link]))
        print(f"✅ Найдено {len(full_links)} объявлений от частных лиц")
        return full_links

    except Exception as e:
        print("❌ Ошибка при загрузке объявлений:", e)
        return []


# === Отправка сообщения по варианту 1 ===
def send_message_variant_1(page, ad_url):
    print(f"📩 Отправляем сообщение по объявлению: {ad_url}")
    try:
        page.goto(ad_url + "/contact")
        time.sleep(random.uniform(4, 7))

        messages = [
            "Здравствуйте!",
            "Понравилось ваше объявление!",
            "Еще продаете?",
            "Скажите, вы риелтор?"
        ]

        message_box = page.locator("#message-textarea")

        for msg in messages:
            message_box.fill(msg)
            page.click("button[form='message-form']")
            print(f"📨 Отправлено: {msg}")
            time.sleep(random.uniform(2, 4))
        print("✅ Сообщение успешно отправлено\n")
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}\n")


# === Основная функция запуска бота ===
def main():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    ua = random.choice(user_agents)
    print(f"🌍 Используем User-Agent: {ua}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(user_agent=ua)
        page = context.new_page()

        if not login_avito(page):
            print("❌ Авторизация не пройдена")
            return

        ads = get_private_ads(page)
        sent_count = 0

        for ad in ads:
            if sent_count >= MAX_MESSAGES:
                print("⚠️ Достигнут лимит в 20 сообщений за день.")
                break
            try:
                send_message_variant_1(page, ad)
                sent_count += 1
                time.sleep(random.uniform(10, 15))
            except Exception as e:
                print(f"❌ Ошибка при работе с объявлением {ad}: {e}")

        print(f"✅ Сегодня отправлено: {sent_count} сообщений")

        context.close()
        browser.close()


# === Запуск скрипта ===
if __name__ == "__main__":
    main()