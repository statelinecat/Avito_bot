import requests
from config import BASE_URL, HEADERS
from auth import load_cookies, update_cookies
import time

def get_session_with_cookies():
    cookies = load_cookies()
    if not cookies:
        update_cookies()
        cookies = load_cookies()
        if not cookies:
            raise Exception("Не удалось загрузить cookies.")

    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    session.headers.update(HEADERS)
    return session

def parse_ads(session):
    url = f"{BASE_URL}/rossiya?q=квартира&user=1"
    response = session.get(url)
    if "data-marker=\"item\"" not in response.text:
        print("Cookies возможно устарели. Пробуем обновить...")
        update_cookies()
        session = get_session_with_cookies()
        response = session.get(url)

    if response.ok:
        print("Парсинг успешен!")
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
    else:
        print("Ошибка при парсинге:", response.status_code)
