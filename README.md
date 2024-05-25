# VkAnalyser

## *Описание проекта*:
Данный сервис представляет из себя веб-платформу для анализа соцсетей. Наш сервис рассчитан на импорт данных от аккаунта, визуализацию его интересов, паттернов и экспорт отчета. В данном проекте реализована регистрация на сайте с хэшированием пароля, парсинг данных аккаунта вк, визуализция интересов, статистик и общей информации в виде дашборда с графиками.


## *Установка и начало работы*

- Создать виртуальное окружение Python (в случае отсутствия)
- Склонировать репозиторий: `git clone https://github.com/dmitriikuleshov/itproject.git`
- Установить зависимости: `pip install -r requirements.txt`
- Произвести миграции базы данных: `python manage.py migrate`
- Установить переменные окружения:
    - `VK_TOKEN` Ключ доступа VK API ([Получить](https://vkhost.github.io))
    - `GIGACHAT_TOKEN` Ключ доступа GigaChat API ([Получить](https://developers.sber.ru/docs/ru/gigachat/individuals-quickstart))
- Запустить сервер: `python manage.py runserver`

## *Работа веб-платформы:*
Наш сервис позволит вам проанализировать ваш или чужой аккаунт в соцсети вконтакте.
Первым делом вам предстоит зарегистрироваться:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Регистрация.gif)

Затем вам следует выбрать заинтересовавший вас аккаунт и ввести ссылку на него в строку поиска. После непродолжительной загрузки в первую очередь вы увидите имя и фамилию пользователя, фотографию профиля, основную информацию и выжимку об аккаунте от нейросети GIGACHAT:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Поиск.gif)

Если это не первый раз, когда вы используете наш сервис, вы можете сразу выбрать аккаунт, который уже изучали из истории:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/История.gif)

Благодаря нашему сервису вы можете увидеть:

Подписки пользователя:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Подписки.gif)

Граф дружеских связей:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Граф%20связей.gif)

График активности пользователя:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/График%20активности.gif)

Анализ токсичности пользователя с ссылками на токсичные посты:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Токсичность.png)

Рекомендацию по знакомствам от нейросети GIGACHAT:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Рекомендации%20знакомств.gif)

Также наша веб-платформа предлагает вам как светлую, так и тёмную тему:

![Alt Text](https://github.com/dmitriikuleshov/itproject/blob/main/docs/media/Смена%20темы.gif)


## *Структура Django-проекта*:

- ***[authentication](authentication)*** Приложение, отвечающее за регистрацию, 
аутентификацию и сохранение учётной информации о пользователях в базе данных.
    - ***[templates](authentication/templates)***
        
        - ***[registration.html](authentication/templates/authentication/registration.html)*** Форма регистрации.
        - ***[login.html](authentication/templates/authentication/login.html)*** Форма для входа в систему.
    - ***[admin.py](authentication/admin.py)***
        
        - `class UserAdmin` Настройка видимости даты регистрации на панели администратора.
    - ***[forms.py](authentication/forms.py)***

        - `class UserForm` Обработка формы регистрации пользователя на странице [authentication.html](authentication/templates/authentication/authentication.html).
        - `class LoginForm` Обработка формы входа в систему на странице [login.html](authentication/templates/authentication/login.html).
    - ***[models.py](authentication/models.py)*** 
        
        - `class User` Обработка модели базы данных, обеспечивающей аутентификацию пользователя.
    - ***[urls.py](authentication/urls.py)*** URL приложения:

        - `<domain>/auth` - регистрация.
        - `<domain>/auth/login` - вход в систему.
        - `<domain>/auth/change_theme` - изменение темы.
    - ***[views.py](authentication/views.py)***

        - `auth_view()` Проверка корректности, охранение записи о пользователе, первичный вход в систему.
        - `login_view()` Проверка корректности и авторизация.
        - `change_theme()` Изменение цветовой палитры.


- ***[main](main)*** Приложение, отвечающее за отображение главной страницы, приветствие, вывод строки ввода url пользователя VK.
    - ***[templates](main/templates)***

        - ***[index.html](main/templates/main/auth-index.html)*** Главная страница, вывод приветствия и предложения войти/зарегистрироваться.
        - ***[auth-ndex.html](main/templates/main/auth-index.html)*** Главная страница, вывод строки ввода ссылки на
        профиль и списка ранее просмотренных ссылок.
    - ***[admin.py](main/admin.py)***

        - `class VkAccount` Настройка видимости даты добавления ссылки на аккаунт VK на панели администратора.
    - ***[models.py](main/models.py)***

        - `class VkAccount` обработка модели базы данных, сохраняющей ссылку на проанализированный аккаунт
        и автора запроса на анализ для дальнейшего вывода ссылок на главной странице.
    - ***[urls.py](main/urls.py)*** URL приложения:
        - `<domain>` Главная страница.
        - `<domain>/logout` Выход из учётной записи.
        - `<domain>/change_theme` Выход из учётной записи.

    - ***[views.py](main/views.py)***

        - `index_view()` Вывод главной страницы.
        - `logout_view()` Выход из учётной записи и перенаправление на главную страницу.
        - `change_theme()` Изменение цветовой палитры.

- ***[vkapi](vkapi)*** Приложение, отвечающее за анализ профиля VK и вывод информации.
    - ***[templates](vkapi/templates)***

        - ***[acquaintances.html](vkapi/templates/vkapi/acquaintances.html)*** Шаблон фрейма с аккаунтами для знакомств.
        - ***[loader.html](vkapi/templates/vkapi/loader.html)*** Шаблон анимации загрузки фрейма.
        - ***[subscriptions.html](vkapi/templates/vkapi/subscriptions.html)*** Шаблон фрейма со списком подписок пользователя.
        - ***[toxicity.html](vkapi/templates/vkapi/toxicity.html)*** Шаблон фрейма с данными о токсичности пользователя.
        - ***[user-info.html](vkapi/templates/vkapi/user-info.html)*** Страница вывода информации о профиле VK.
    
    - ***[gigachat_tools.py](vkapi/gigachat_tools.py)***
        - `check_acquaintances` Проверка двух пользователей ВК на возможность знакомства с помощью GigaChat.
        - `get_written_squeeze` Получение письменной выжимки информации о пользователе с помощью GigaChat.
    - ***[toxicity_check.py](vkapi/toxicity_check.py)***
        - `check_obscene_vocabulary` Проверка списка входящих строк на предмет наличия нецензурной или оскорбительной 
лексики по онлайн-базе. Возврат списка тех строк, в которых она была найдена.
    - ***[visualization.py](vkapi/visualization.py)***
        - `class Visualisation` Методы создания графов, графиков и прочей аналитики в HTML-формате.
    - ***[vk_tools_models.py](vkapi/toxicity_check.py)*** Информационные модели для работы с API ВК.
    
    - ***[vk_tools.py](vkapi/vk_tools.py)***

        - `class Vk` Класс, отвечающий за подключение к API VK и обработку получаемой информации.

    - ***[urls.py](vkapi/urls.py)*** URL приложения:

        - `<domain>/vk` Вывод информации о пользователе.
        -  `<domain>/vk/mutual-friends` Граф дружеских связей.
        - `<domain>/vk/activity` График активности.
        - `<domain>/vk/subscriptions` Информация о подписках.
        - `<domain>/vk/change-theme` Изменение цветовой палитры.
        - `<domain>/vk/toxicity` Информация о токсичности.
        - `<domain>/vk/acquaintances` Информация о возможных знакомствах.
        - `<domain>/vk/loader` Анимация загрузки
    - ***[views.py](vkapi/views.py)*** 

        - `user_info_view()` Получение ссылки на профиль, переданной с главной страницы и вывод нужной информации.
        - И другие обработчики описанных выше фреймов.

## *[Ссылка на доску Канбан](https://luminous-epoch-ab9.notion.site/34f0826e8fbf44a9bea7956946d513f3?v=406f7bea22c641e9ba46695d09633b9a)*
    
## *Список источников информации*:
- https://habr.com/ru/articles/221251/
- https://dev.vk.com/ru/method
- https://www.kaggle.com/code/ludovicocuoghi/twitter-sentiment-analysis-with-bert-vs-roberta
- https://habr.com/ru/articles/221251/
- https://youtube.com/playlist?list=PLDyJYA6aTY1nZ9fSGcsK4wqeu-xaJksQQ&si=6sWDR4eWMm0U78eU
- https://www.youtube.com/playlist?list=PLBheEHDcG7-nyRX-kMT2jyudahDQ-A-Ss
- https://habr.com/ru/companies/ruvds/articles/705368/
- https://roadmap.sh/frontend
- https://learn.javascript.ru
- https://developer.mozilla.org/ru/docs/Web/JavaScript
- https://doka.guide/js/
## *Команда разработчиков*:
- **Фролов Вячеслав**, Руководитель команды, фронтенд
- **Кулешов Дмитрий**, Технический руководитель, визуализация данных, бэкенд
- **Власко Михаил**, Разработка серверной части проекта
- **Григорьев Тимофей**, Разработка серверной части проекта
- **Попов Александр**, Фронтенд
------------------

*Москва, МАИ, 2024*
