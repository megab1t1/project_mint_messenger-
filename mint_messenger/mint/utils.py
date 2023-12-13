menu = [
    {'title': 'аккаунт', 'url': 'account', 'id': 1},
    {'title': 'сообщения', 'url': 'chats', 'id': 2},
    {'title': 'друзья', 'url': 'friends', 'id': 3}
]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['menu'] = menu

        return context
