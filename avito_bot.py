import asyncio
import random
import sqlite3
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Конфигурация
DB_PATH = 'avito_messages.db'
CITY_URL = 'https://www.avito.ru/kostroma/nedvizhimost'
HEADLESS = False
MAX_ADS = 5
DELAY_BETWEEN_ACTIONS = 5

# Папка для логов
DEBUG_DIR = 'debug_logs'
os.makedirs(DEBUG_DIR, exist_ok=True)

# Сообщения
MESSAGE_VARIANTS = [
    ["Здравствуйте!", "Заинтересовало ваше объявление.", "Еще актуально?"],
    ["Добрый день!", "Понравилось ваше предложение.", "Еще продаете?"]
]


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                ad_id TEXT PRIMARY KEY,
                seller_id TEXT,
                chat_url TEXT,
                last_message_time DATETIME,
                responded INTEGER DEFAULT 0,
                reminded INTEGER DEFAULT 0
            )
        ''')


def save_message(ad_id, seller_id, chat_url):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            INSERT OR IGNORE INTO messages (ad_id, seller_id, chat_url, last_message_time)
            VALUES (?, ?, ?, datetime('now'))
        ''', (ad_id, seller_id, chat_url))


async def save_screenshot(page, prefix="debug"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(DEBUG_DIR, f"{prefix}_{timestamp}.png")
    await page.screenshot(path=path, full_page=True)
    log(f"📸 Скриншот сохранен: {path}")


async def click_write_message_button(page):
    try:
        # Основной селектор для кнопки "Написать сообщение"
        write_button = await page.wait_for_selector(
            "button:has-text('Написать сообщение')",
            timeout=15000
        )

        if not write_button:
            log("❌ Кнопка не найдена по основному селектору")
            return False

        log("🖱️ Нажимаем кнопку 'Написать сообщение'")
        await write_button.click()
        await page.wait_for_timeout(DELAY_BETWEEN_ACTIONS * 1000)

        # Проверяем, открылся ли чат
        chat_loaded = await page.wait_for_selector(
            "textarea[data-marker='message-input']",
            timeout=15000
        )
        if not chat_loaded:
            log("❌ Чат не открылся после нажатия кнопки")
            await save_screenshot(page, "chat_not_opened")
            return False

        return True
    except Exception as e:
        log(f"⚠️ Ошибка при нажатии кнопки: {e}")
        await save_screenshot(page, "click_error")
        return False


async def send_messages_to_chat(page):
    try:
        textarea = await page.query_selector("textarea[data-marker='message-input']")
        if not textarea:
            log("❌ Поле ввода сообщения не найдено")
            return False

        messages = random.choice(MESSAGE_VARIANTS)
        for msg in messages:
            await textarea.fill(msg)
            await textarea.press("Enter")
            log(f"✉️ Отправлено: {msg}")
            await page.wait_for_timeout(DELAY_BETWEEN_ACTIONS * 1000)

        return True
    except Exception as e:
        log(f"⚠️ Ошибка при отправке сообщений: {e}")
        await save_screenshot(page, "send_error")
        return False


async def process_advertisement(page, ad_url):
    try:
        log(f"🔗 Обрабатываем объявление: {ad_url}")
        await page.goto(ad_url, timeout=60000)
        await page.wait_for_timeout(DELAY_BETWEEN_ACTIONS * 1000)

        # Пропускаем объявления компаний
        company_check = await page.query_selector("text=Компания")
        if company_check:
            log("⏭️ Пропускаем объявление компании")
            return False

        # Нажимаем кнопку "Написать сообщение"
        if not await click_write_message_button(page):
            return False

        # Отправляем сообщения
        if not await send_messages_to_chat(page):
            return False

        # Сохраняем информацию о чате
        chat_url = page.url
        seller_id = chat_url.split('/')[-2]
        ad_id = ad_url.split('_')[-1].split('?')[0]
        save_message(ad_id, seller_id, chat_url)

        return True
    except Exception as e:
        log(f"⚠️ Ошибка при обработке объявления: {e}")
        await save_screenshot(page, "ad_error")
        return False


async def collect_ad_links(page):
    try:
        await page.goto(CITY_URL, timeout=60000)
        await page.wait_for_selector("div[data-marker='item']", timeout=15000)

        ad_elements = await page.query_selector_all("div[data-marker='item']")
        ad_links = []

        for el in ad_elements[:MAX_ADS]:
            link = await el.query_selector("a[itemprop='url']")
            if link:
                href = await link.get_attribute("href")
                full_url = f"https://www.avito.ru{href}"
                ad_links.append(full_url)

        log(f"🔍 Найдено {len(ad_links)} объявлений")
        return ad_links
    except Exception as e:
        log(f"⚠️ Ошибка при поиске объявлений: {e}")
        await save_screenshot(page, "ads_error")
        return []


async def run_bot():
    log("🚀 Запускаем бота")
    init_db()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--start-maximized"] if not HEADLESS else []
        )

        context = await browser.new_context(
            viewport=None if not HEADLESS else {"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            storage_state='avito_cookies.json' if os.path.exists('avito_cookies.json') else None
        )

        page = await context.new_page()

        try:
            ad_links = await collect_ad_links(page)
            if not ad_links:
                log("❌ Не найдено объявлений для обработки")
                return

            for ad_url in ad_links:
                success = await process_advertisement(page, ad_url)
                if success:
                    log(f"✅ Успешно обработано: {ad_url}")
                else:
                    log(f"❌ Не удалось обработать: {ad_url}")

                await page.wait_for_timeout(DELAY_BETWEEN_ACTIONS * 1000 * 2)

        except Exception as e:
            log(f"🚨 Критическая ошибка: {e}")
            await save_screenshot(page, "critical_error")
        finally:
            await context.storage_state(path="avito_cookies.json")
            await browser.close()
            log("🏁 Работа бота завершена")


if __name__ == '__main__':
    asyncio.run(run_bot())