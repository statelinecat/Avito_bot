from playwright.sync_api import sync_playwright
import json

def save_avito_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Переход на страницу профиля
        page.goto("https://www.avito.ru/profile")
        print("👉 Залогиньтесь вручную в открывшемся окне...")

        # Ждём, пока пользователь залогинится
        page.wait_for_url("https://www.avito.ru/profile",  timeout=60_000)

        # Сохраняем куки
        cookies = context.cookies()
        with open("avito_cookies.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f)
        print("✅ Куки сохранены в файл 'avito_cookies.json'")

        context.close()

if __name__ == "__main__":
    save_avito_cookies()