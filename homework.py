from http import HTTPStatus
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
    HomeworkApiError, APIStatusCodeError
)


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 300
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'{PRACTICUM_TOKEN}'}
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'reviewing': 'Работа взята на проверку ревьюером.',
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
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
    current_timestamp: int
) -> Dict[str, List[Dict[str, Union[int, float, str]]]]:
    """Делает запрос к API яндекса и возвращает ответ."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    headers = HEADERS
    try:
        logging.info('Запрашивает информацию о домашках')
        homework_statuses = requests.get(URL, headers=headers, params=params)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise APIStatusCodeError(
                'Неверный ответ сервера: '
                f'http code = {homework_statuses.status_code}; '
                f'reason = {homework_statuses.reason}; '
                f'content = {homework_statuses.text}'
            )
    except Exception as exc:
        error_message = f'Ошибка подключения к API яндекса: {exc}'
        logging.exception(error_message)
        raise HomeworkApiError(error_message) from exc
    else:
        return homework_statuses.json()


def check_response(
    response: Dict[str, List[Dict[str, Union[int, float, str]]]]
) -> Dict[str, Union[int, float]]:
    """Проверяет наличие домашки."""
    if not isinstance(response, dict):
        error_message = (
            'Ответ от API не является словарем:'
            f'response = {response}')
        logging.exception(error_message)
        raise TypeError(error_message)

    if not response:
        raise TypeError('В ответе пришёл пустой список')

    if not all(['current_date' in response, 'homeworks' in response]):
        raise KeyError('В ответе API нет нужных ключей')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Homeworks не список')
    return response['homeworks'][0]


def parse_status(homework: Dict[str, Union[int, float, str]]) -> str:
    """Проверяет статус домашки."""
    try:
        homework_name = homework['homework_name']
    except Exception:
        error_message = 'В ответе API отсутствуют нужные ключи '

        logging.exception(error_message)
        raise KeyError(error_message)
    try:
        homework_status = homework['status']
    except Exception:
        error_message = 'В ответе API отсутствуют нужные ключи '

        logging.exception(error_message)
        raise KeyError(error_message)
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception:
        error_message = 'Недокументированный статус домашней работы'

        logging.exception(error_message)
        raise KeyError(error_message)

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет наличие всех переменных окружения."""
    return all((
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
    ))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = (
            'Отсутствуют обязательные переменные окружения: '
            'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,'
            'Программа принудительно остановлена'
        )
        logging.critical(error_message)
        sys.exit(error_message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    current_report = None
    prev_report = current_report

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks is None:
                logging.debug('Нет новых домашек')
                time.sleep(RETRY_TIME)
                continue
            answer = parse_status(homeworks)
            current_report = answer
            if current_report == prev_report:
                logging.debug(
                    'Нет обновлений по статутсу домашки'
                )
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            current_report = error_message
        try:
            if current_report != prev_report:
                send_message(bot, current_report)
                prev_report = current_report
        except TelegramError as exc:
            error_message = f'Сбой в работе программы: {exc}'
            logging.exception(error_message)
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
