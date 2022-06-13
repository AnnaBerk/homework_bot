from datetime import datetime, timedelta
import logging
import os
import sys
import time
from dotenv import load_dotenv
import requests
import telegram 
from telegram import Bot, TelegramError
from typing import Dict, List, Union

from exceptions import (
    HomeworkApiError
)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: Bot, message: str) -> None:
    """Отправляет сообщение в телеграм."""
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
    }
    try:
        logging.info('Отправляем сообщение в телеграм: %s', message)
        bot.send_message(**data)
    except TelegramError as exc:
        error_message = f'Ошибка отправки сообщения в телеграм: : {exc}'
        logging.exception(error_message)
    else:
        logging.info('Сообщение в телеграм успешно отправлено')    


def get_api_answer(
    current_timestamp: int) -> Dict[str, List[Dict[str, Union[int, float, str]]]]:
    """Делает запрос к API яндекса и возвращает ответ."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': PRACTICUM_TOKEN}
    try:
        logging.info('Запрашивает информацию о домашках')
        homework_statuses = requests.get(URL, headers=headers, params=params)
    except Exception as exc:
        error_message = f'Ошибка подключения к API яндекса: {exc}'
        logging.exception(error_message)
        raise HomeworkApiError(error_message) from exc
    else:
        return homework_statuses.json()


def check_response(
    response: Dict[str, List[Dict[str, Union[int, float, str]]]]) -> List[str]:
    """Проверяет наличие домашки."""
    if not isinstance(response, Dict):
        error_message = f'Ответ от API не является словарем: response = {response}'
        logging.exception(error_message)
        raise TypeError(error_message)
    try:     
        homework = response['homeworks'][0]
        
    except Exception as exc:
        error_message = f'Нет такого индекса в списке: {exc}'
        logging.exception(error_message)
        raise IndexError(error_message) from exc 
    return homework
  

def parse_status(homework: str) -> str:
    try:
        homework_name = homework['homework_name']
    except Exception: 
        error_message = 'В ответе API отсутствуют необходимый ключ "homework_name", '
        f'homework = {homework}'
        logging.exception(error_message)   
        raise HomeworkApiError(error_message) 
    try:
        homework_status = homework['status']
    except Exception: 
        error_message = 'В ответе API отсутствуют необходимый ключ "homework_status", '
        f'homework = {homework}'
        logging.exception(error_message)   
        raise HomeworkApiError(error_message) 


    for status, answer in HOMEWORK_STATUSES.items():
        if homework_status==status:
            verdict = answer
        
    print(verdict)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения"""
    return all((
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
    ))

def main():
    """Основная логика работы бота."""
  
    if not check_tokens():
        error_message = (
            f'Отсутствуют обязательные переменные окружения: '
            'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,'
            'Программа принудительно остановлена'
        )
        sys.exit(error_message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())

        
    current_report = None
    prev_report = current_report
  
    while True:
        try:
            response = get_api_answer(thirty_days_ago)
            homeworks = check_response(response)
            answer = parse_status(homeworks)
            current_report = answer
            

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            current_report = error_message
        try:
            if current_report != prev_report:
                send_message(bot, current_report)
                prev_report = current_report
        except TelegramError as exc:
            error_message = f'Сбой в работе программы: {exc}'
            

        time.sleep(RETRY_TIME)
      

if __name__ == '__main__':
    log_format = (
        '%(asctime)s [%(levelname)s] - '
        '(%(filename)s).%(funcName)s:%(lineno)d - %(message)s'
    )
    log_stream = sys.stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[logging.StreamHandler(log_stream)]
    )
    main()
