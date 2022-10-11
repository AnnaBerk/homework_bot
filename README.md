#  Homework Bot

### Описание
Простой бот работающий с API Яндекс.Практикум, весь функционал это отображать статус проверки кода ревью вашей работы.
Достаточно запустить бота, прописать токены. Каждые 10 минут бот проверяет API Яндекс.Практикум и присылает в телеграм статус. Если работа проверена вы получите сообщение о статусе вашего код ревью.

Пример ответа бота - ассистента:
```bash
{
   "homeworks":[
      {
         "id":12,
         "status":"approved",
         "homework_name":"annaBerk__homework_bot-master.zip",
         "reviewer_comment":"Работа принята",
         "date_updated":"2022-06-14T14:30:57Z",
         "lesson_name":"Проект 6 спринта"
      }
   ],
   "current_date":1581805098
}
```
У API Практикум.Домашка есть лишь один эндпоинт:
```bash
https://practicum.yandex.ru/api/user_api/homework_statuses/
```
Доступ к нему возможен только по токену.

### Установка

Клонировать репозиторий:
```bash
git clone git@github.com:AnnaBerk/homework_bot.git
```
Перейти в папку с проектом:
```bash
cd homework_bot/
```
Установить виртуальное окружение для проекта:
```bash
python -m venv venv
```
Активировать виртуальное окружение для проекта:

для OS Lunix и MacOS
```bash
source venv/bin/activate
```
для OS Windows
```bash
source venv/Scripts/activate
```
Установить зависимости:
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнить миграции на уровне проекта:
```bash
cd yatube
python3 manage.py makemigrations
python3 manage.py migrate
```
Зарегистрировать чат-бота в Телеграм:
```bash
pip install -r requirements.txt
```
Создать в корневой директории файл .env для хранения переменных окружения
```bash
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```
Запустить проект локально:
```bash
для OS Lunix и MacOS
python homework_bot.py
```
```bash
для OS Windows
python3 homework_bot.py
```
Бот будет работать, и каждые 10 минут проверять статус вашей домашней работы.
