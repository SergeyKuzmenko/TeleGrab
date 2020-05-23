from telethon import TelegramClient, errors
from telethon.tl.functions.contacts import ResolveUsernameRequest

from configparser import ConfigParser
from prettytable import PrettyTable
import logging
import os
import pathlib
import sys

# Другие настройки
config = ConfigParser()
logging.basicConfig(filename='.log', filemode='a', format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.DEBUG)
configFile = pathlib.Path('config.ini')

# Проверка наличия файла с данными
if configFile.exists():
    # Инициализация клиента
    try:
        config.read('config.ini')
        api_id = config.get('telegram', 'api_id')
        api_hash = config.get('telegram', 'api_hash')
        client = TelegramClient('telegram', api_id, api_hash).start()
    except errors.rpcerrorlist.ApiIdInvalidError:
        print('[Ошибка] Введенны неверные данные api_id/api_hash')
        os.remove('config.ini')
        input()
else:
    # Инструкция как получить api_id и api_hash
    # ==============================
    print('Чтобы начать работать с программой нужно выполнить несколько действий: ')
    print('1) Для начала нам нужно получить api_id и api_hash.')
    print('   Для этого нужно зайти на https://my.telegram.org/ и авторизироваться.')
    print('2) Далее нужно создать новое приложение с любыми параметрами.')
    print('3) После создания приложения перейдите в раздел "API development tools",')
    print('   в секции "App configuration" будут нужные данные (api_id и api_hash).')
    # ==============================
    # Создание файла и запись данных
    input_api_id = input('Введите api_id: ')
    input_api_hash = input('Введите api_hash: ')

    try:
        api_id = int(input_api_id)
        api_hash = str(input_api_hash)

        config.read('config.ini')
        config.add_section('telegram')
        config.set('telegram', 'api_id', str(api_id))
        config.set('telegram', 'api_hash', str(api_hash))

        # Запись файла конфигурации
        with open('config.ini', 'w') as f:
            config.write(f)
        # Инициализация клиента
        try:
            client = TelegramClient('telegram', api_id, api_hash).start()
        except errors.rpcerrorlist.ApiIdInvalidError:
            print('[Ошибка] Неправильная комбинация api_id / api_hash (вызвана SendCodeRequest)')
            print('[Ошибка] Проверьте правильность ввода данных и повторите еще')
            os.remove('config.ini')
            input()
    except ValueError:
        print('[Ошибка] Введены не валидные данные: api_id или api_hash')
        print('[Ошибка] api_id должно быть целым числом, а api_hash строкой')
        input()
        # os.remove('config.ini')

# Загрузка информации о текущем профиле
async def me():
    me = await client.get_me()
    me_table = PrettyTable(['Параметр', 'Значение'])
    me_table.align["Параметр"] = "l"
    me_table.align["Значение"] = "l"
    me_table.add_row(['Имя', str(me.first_name)])
    me_table.add_row(['Логин', str(me.username)])
    me_table.add_row(['Телефон', str(me.phone)])
    me_table.add_row(['id', str(me.id)])
    me_table.add_row(['access_hash', str(me.access_hash)])
    print(me_table)

# Загрузка всех диалогов (их id)
async def dialogs():
    dialogs_table = PrettyTable(['id', 'Название'])
    dialogs_table.align["id"] = "l"
    dialogs_table.align["Название"] = "l"
    async for dialog in client.iter_dialogs():
        if dialog.id > 0:
            dialogs_table.add_row([dialog.id, dialog.title])
    print(dialogs_table)

async def channels():
    dialogs_table = PrettyTable(['id', 'Название'])
    dialogs_table.align["id"] = "l"
    dialogs_table.align["Название"] = "l"
    async for channel in client.iter_dialogs():
        if channel.id < 0:
            dialogs_table.add_row([channel.id, channel.title])
    print(dialogs_table)

# Загрузка списка подписчиков с выбраного чата/канала
async def users(inputId):
    users = await client.get_participants(inputId, limit=5000, aggressive=1)
    users_table = PrettyTable(['id', 'Логин', 'Имя'])
    users_table.align["id"] = "l"
    users_table.align["Логин"] = "l"
    users_table.align["Имя"] = "l"
    with open('telegram_users_' + str(inputId) + '.csv', 'w', encoding='utf-8') as f:
        for user in users:
            f.write(str(user.id) + ',' + str(user.username) + ',' + str(user.first_name) + '\n')
            users_table.add_row([user.id, user.username, user.first_name])
    print(users_table)
    print('Данные сохранены в файл: '+ str(os.path.abspath(os.getcwd())) +'\\telegram_users_' + str(inputId) + '.csv')
    f.close()

def send_msg(msg):
    return client.send_message('@sergey_kuzmenko', str(msg))


def show_menu():
    print('Список доступных команд: ')
    action_table = PrettyTable(['Команда', 'Описание'])
    action_table.align["Команда"] = "l"
    action_table.align["Описание"] = "l"
    action_table.add_row(['me', 'Загрузка информации о текущем профиле'])
    action_table.add_row(['dialogs', 'Загрузка списка доступных диалогов (id : Название)'])
    action_table.add_row(['channels', 'Загрузка списка доступных каналов (id : Название)'])
    action_table.add_row(['users', 'Загрузка списка подписчиков с выбраного диалога/канала'])
    # action_table.add_row(['contact', 'Написать разработчику приложения'])
    action_table.add_row(['exit', 'Выйти из программы'])
    print(action_table)

def get_action():
    while True:
        action = input('Введите команду: ')
        if action == 'me':
            print('Результат выполения: ')
            client.loop.run_until_complete(me())
            break
        if action == 'dialogs':
            print('Результат выполения: ')
            client.loop.run_until_complete(dialogs())
            break
        if action == 'channels':
            print('Результат выполения: ')
            client.loop.run_until_complete(channels())
            break
        if action == 'users':
            try:
                id = int(input('Введите id диалога/канала: '))
                if id:
                    try:
                        print('Результат выполения: ')
                        client.loop.run_until_complete(users(id))
                    except Exception as e:
                        print('Error: ' + str(e))
                break
            except:
                print('[Ошибка] Недопустимый вариант id')
                input()
                break
            break
        if action == 'contact':
            print('Если есть какие-то вопросы, идеи или приложения - напишите мне.')
            print('Если меня это заинтересует я дам об этом знать :)')
            while True:
                message = input('Введите Ваше сообщение: ')
                if message:
                    client.parse_mode = 'html'
                    send_msg(str(message))
                    print('Сообщение отправленно!')
                    input()
                    break
            break
        if action == 'exit':
            exit()
            break
        else:
            print('[Ошибка] Неизвестная команда, попробуйте еще раз...')

def main():
    show_menu()
    while True:
        print('#===============================================================#')
        get_action()

with client:
    main()