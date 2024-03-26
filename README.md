# VkAnalyser

-----------------------

### *Структура Django-проекта*:

- ***[authentication](authentication)*** Приложение, отвечающее за регистрацию, 
аутентификацию и сохранение учётной информации о пользователях в базе данных.
    - ***[templates](authentication/templates)***
        
        - ***[authentication.html](authentication/templates/authentication/authentication.html)*** Форма регистрации.
        - ***[layout.html](authentication/templates/authentication/layout.html)*** Основа для шаблонов приложения.
        - ***[login.html](authentication/templates/authentication/login.html)*** Форма для входа в систему.
        - ***[successfully.html](authentication/templates/authentication/successfully.html)*** Страница с сообщением об
        успешной регистрации.
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
    - ***[views.py](authentication/views.py)***

        - `auth_view()` Проверка корректности, охранение записи о пользователе, первичный вход в систему.
        - `login_view()` Проверка корректности и авторизация.


- ***[main](main)*** Приложение, отвечающее за отображение главной страницы, приветствие, вывод строки ввода url пользователя VK.
    - ***[templates](main/templates)***

        - ***[index.html](main/templates/main/index.html)*** Главная страница, вывод приветствия и строки ввода ссылки на
        профиль или ссылок на регистрацию и авторизацию в зависимости от состояния.
    - ***[forms.py](main/forms.py)***

        - `class LinkForm` Форма ввода ссылки на аккаунт VK, предлагаемый для анализа.
    - ***[urls.py](main/urls.py)*** URL приложения:

        - `<domain>` Главная страница.
        - `<domain>/logout` Выход из учётной записи.
    - ***[views.py](main/views.py)***

        - `index_view()` Вывод главной страницы.
        - `logout_view()` Выход из учётной записи и перенаправление на главную страницу.


- ***[vkapi](vkapi)*** Приложение, отвечающее за анализ профиля VK и вывод информации.
    - ***[templates](vkapi/templates)***

        - ***[layout.html](vkapi/templates/vkapi/layout.html)*** Основа для шаблонов приложения.
        - ***[user-info.html](vkapi/templates/vkapi/user-info.html)*** Страница вывода информации о профиле VK.
    - ***[tools.py](vkapi/tools.py)***

        - `class Vk` Класс, отвечающий за подключение к API VK и обработку получаемой информации.
            - `get_id_from_link` Получение id пользователя по ссылке на его профиль.
            - `get_info` Получение словаря с основными данными о профиле с помощью API-метода `Users.Get`.
    - ***[urls.py](vkapi/urls.py)*** URL приложения:

        - `<domain>/vk` Вывод информации о пользователе.
    - ***[views.py](vkapi/views.py)*** 

        - `user_info_view()` Обработка формы `LinkForm`, переданной с главной страницы и вывод нужной информации.

------------------

*Москва, МАИ, 2024*