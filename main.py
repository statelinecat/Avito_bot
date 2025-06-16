from avito_parser import get_session_with_cookies, parse_ads
from auth import update_cookies
import time

def main():
    try:
        session = get_session_with_cookies()
        while True:
            parse_ads(session)
            print("Ожидание 1 час до следующего запуска...")
            time.sleep(3600)
    except Exception as e:
        print("Ошибка:", e)
        update_cookies()

if __name__ == "__main__":
    main()
