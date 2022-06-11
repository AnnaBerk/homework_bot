from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv
import requests
import telegram 

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    ...


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': PRACTICUM_TOKEN}
    homework_statuses = requests.get(URL, headers=headers, params=params)
    # print(homework_statuses.json())
    return homework_statuses.json()


def check_response(response):
    if response:
        print(response['homeworks'])
        return response['homeworks']



def parse_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']

    for status, answer in HOMEWORK_STATUSES.items():
        if homework_status==status:
            verdict = answer
        
    print(verdict)
    # verdict = ...

    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения"""
    # if "PRACTICUM_TOKEN" in os.environ:
    #     return True
    # return False    
    return all((
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
    ))

def main():
    """Основная логика работы бота."""
  
    if check_tokens():
        print('трумс')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
    response = get_api_answer(thirty_days_ago)
    homeworks = check_response(response)
    parse_status(homeworks[0])
  
    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
