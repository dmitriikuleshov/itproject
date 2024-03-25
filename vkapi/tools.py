import vk_api
import re


class Vk:
    """Класс, отвечающий за подключение VK API."""

    def __init__(self, token: str) -> None:
        """
        Инициализация токена VK.
        :param token: str
        """
        self.__vk = vk_api.VkApi(token=token).get_api()

    def get_id_from_link(self, link: str) -> str:
        """
        Метод, возвращающий ID пользователя по ссылке на его профиль.
        :param link: str
        :return: str
        """
        id_reg_expression = (r"(^-?[\d]+)|(?:feed\?\w?=)?(?:wall|im\?sel="
                             r"|id=*|photo|videos|albums|audios|topic)(-?"
                             r"[\d]+)|(?:club|public)([\d]*)|(?<=\.com/)("
                             r"[a-zA-Z\d._]*)")
        find_results = re.findall(id_reg_expression, link)
        id_or_name = None
        if find_results:
            try:
                id_or_name = [el for el in find_results[0] if el]
                user_id = int(id_or_name[0])
            except ValueError:
                try:
                    resolved_name = self.__vk.utils.resolveScreenName(
                        screen_name=id_or_name[0])
                    user_id = resolved_name['object_id'] if resolved_name['type'] != 'application' else None
                    if user_id is None:
                        raise TypeError
                    if resolved_name['type'] == 'group':
                        user_id = -user_id
                except KeyError:
                    raise TypeError
            return user_id
        else:
            raise TypeError

    def get_info(self, link: str) -> dict:
        """
        Метод, возвращающий полную информацию о пользователе по ссылке.
        :param link: str
        :return: dict
        """
        return self.__vk.users.get(user_ids=self.get_id_from_link(link),
                                   fields='photo_id, verified, sex, bdate, '
                                          'city, country, home_town, has_photo, '
                                          'photo_50, photo_100, photo_200_orig, '
                                          'photo_200, photo_400_orig, photo_max, '
                                          'photo_max_orig, online, lists, domain, '
                                          'has_mobile, contacts, site, education, '
                                          'universities, schools, status, last_seen, '
                                          'followers_count, common_count, occupation, '
                                          'nickname, relatives, relation, personal, '
                                          'connections, exports, wall_comments, '
                                          'activities, interests, music, movies, tv, '
                                          'books, games, about, quotes, can_post, '
                                          'can_see_all_posts, can_see_audio, '
                                          'can_write_private_message, can_send_friend_request, '
                                          'is_favorite, is_hidden_from_feed, timezone, screen_name, '
                                          'maiden_name, crop_photo, is_friend, friend_status, '
                                          'career, military, blacklisted, blacklisted_by_me')[0]
