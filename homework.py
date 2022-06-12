from datetime import datetime, timedelta
from http import HTTPStatus
import os
import sys
import time
from dotenv import load_dotenv
import requests
import telegram 
from telegram import Bot, TelegramError
from typing import Dict, List, Union

from exceptions import (
    HomeworkApiError, APIStatusCodeError
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

# MESSAGE = 'homework_name: {homework_name}, verdict: {verdict}'

def send_message(bot: Bot, message: str) -> None:
    """Отправляет сообщение в телеграм."""
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
    }
    try:
        bot.send_message(**data)
    except Exception as exc:
        raise TelegramError(
            f'Ошибка отправки сообщения в телеграм: {exc}'
        ) from exc


def get_api_answer(
    current_timestamp: int) -> Dict[str, List[Dict[str, Union[int, float, str]]]]:
    """Делает запрос к API яндекса и возвращает ответ."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = {'Authorization': PRACTICUM_TOKEN}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=params)
        return homework_statuses.json()
    except Exception as exc:
        raise HomeworkApiError(f'Ошибка подключения к API яндекса: {exc}') from exc
    else:
        return response


def check_response(
    response: Dict[str, List[Dict[str, Union[int, float, str]]]]) -> List[str]:
    """Проверяет наличие домашки."""
    if not isinstance(response, Dict):
        raise TypeError(
            f'Ответ от API не является словарем: response = {response}'
        )
    try:     
        homework = response['homeworks'][0]
        return homework
    except Exception as exc:
        raise IndexError(f'Нет такого индекса в списке: {exc}') from exc #мб надо другую ошибку
    print(homework)
    

def parse_status(homework: str) -> str:
    homework_name = homework['homework_name']
    homework_status = homework['status']

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
    # response = get_api_answer(thirty_days_ago)
    # homeworks = check_response(response)
    # answer = parse_status(homeworks)
    # send_message(bot, answer)
    
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
    main()
