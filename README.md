# VkAnalyser

## *[Ссылка на доску Канбан](https://luminous-epoch-ab9.notion.site/34f0826e8fbf44a9bea7956946d513f3?v=406f7bea22c641e9ba46695d09633b9a)*

## *Работа веб-платформы:*


## *Структура Django-проекта*:

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

        - ***[index.html](main/templates/main/auth-index.html)*** Главная страница, вывод приветствия и строки ввода ссылки на
        профиль или ссылок на регистрацию и авторизацию в зависимости от состояния.
    - ***[admin.py](main/admin.py)***

        - `class VkAccount` Настройка видимости даты добавления ссылки на аккаунт VK на панели администратора.
    - ***[models.py](main/models.py)***

        - `class VkAccount` обработка модели базы данных, сохраняющей ссылку на проанализированный аккаунт
        и автора запроса на анализ для дальнейшего вывода ссылок на главной странице.
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
    
    - ***[toxicity_check.py](vkapi/toxicity_check.py)***
        - `check_obscene_vocabulary` Проверка списка входящих строк на предмет наличия нецензурной или оскорбительной 
лексики по онлайн-базе. Возврат списка тех строк, в которых она была найдена.
    
    - ***[vk_tools.py](vkapi/vk_tools.py)***

        - `class Vk` Класс, отвечающий за подключение к API VK и обработку получаемой информации.
            - `get_id_from_link` Получение id пользователя по ссылке на его профиль.
            - `valid` Статический метод, обеспечивающих проверку существования информации в словарях ответов api,
и установку для отсутствующих значений `None`.
            - `convert_time` Статический метод, преобразующий список моментов времени в формате Unix в эквивалентный
список в обычном формате (`ГГГГ-ММ-ДД ЧЧ:ММ:СС`).
            - `get_info` Получение словаря с основными данными о профиле и списка друзей и подписок с помощью 
API-методов `Users.Get` и `Wall.Get`.
            - `get_links_by_ids` Метод, возвращающий по списку id пользователей или групп список их имён (названий) и
ссылок на их страницы.
            - `get_activity` Метод, для заданного пользователя определяющий моменты времени, в которые он выкладывал
посты на своей странице или оставлял комментарии на страницах друзей, или пользователей или групп, на которые он
подписан. Принимает в качестве аргументов ограничения на количество просматриваемых аккаунтов и на дату публикации 
рассматриваемых постов. Возвращает отсортированный список моментов времени в формате Unix или список текстов постов
в зависимости от параметра.
            - `check_toxicity` Метод, для заданного пользователя проверяющий по удалённой базе данных наличие в его
комментариях и постах нецензурной или оскорбительной лексики. Возвращает список текстов, в которых такая лексика была
найдена.

    - ***[urls.py](vkapi/urls.py)*** URL приложения:

        - `<domain>/vk` Вывод информации о пользователе.
    - ***[views.py](vkapi/views.py)*** 

        - `user_info_view()` Получение ссылки на профиль, переданной с главной страницы и вывод нужной информации.



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
- Фролов Вячеслав, Руководитель команды, фронтенд
- Кулешов Дмитрий, Технический руководитель, визуализация данных, бэкенд
- Власко Михаил, Разработка серверной части проекта
- Григорьев Тимофей, Разработка серверной части проекта
- Попов Александр, Фронтенд
------------------

*Москва, МАИ, 2024*
