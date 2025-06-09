from auth import run_avito_auth
from avito_actions import process_avito_pages
from messenger_handler import check_unread_messages
import time
from datetime import datetime, timedelta


def is_working_hours():
    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=22, minute=00, second=00, microsecond=0)
    return start_time <= now <= end_time


def sleep_until_next_working_day():
    now = datetime.now()
    next_start_time = (now + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
    sleep_duration = (next_start_time - now).total_seconds()
    print(f"Текущее время вне рабочих часов. Ожидание до 8:00 следующего дня ({next_start_time}).")
    time.sleep(sleep_duration)

def reset_daily_state():
    # Очищаем файл с обработанными объявлениями каждый день
    open(PRIVATE_SELLERS_FILE, 'w').close()



if __name__ == "__main__":
    print("Начинаем основную авторизацию...")
    driver = run_avito_auth()

    if driver:
        print("Авторизация прошла успешно. Запускаем основной цикл.")
        while True:
            if is_working_hours():
                from avito_actions import reset_daily_state
                reset_daily_state()  
                print("Начинаем обработку объявлений...")
                process_avito_pages(driver)
                
                
                print(f"Завершена обработка объявлений. Переход к проверке сообщений на 30 минут...")
                message_check_end_time = time.time() + 1 * 3600  
                while time.time() < message_check_end_time and is_working_hours():
                    check_unread_messages(driver)
                    time.sleep(60)
                
                
                if is_working_hours():
                    print("Проверка сообщений завершена. Возвращаемся к парсингу объявлений...")
                    continue  
            else:
                sleep_until_next_working_day()