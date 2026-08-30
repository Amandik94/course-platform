from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Приводит все ошибки DRF к единому формату:
    {"detail": "понятное сообщение"} для простых случаев,
    либо {"field_name": ["ошибка"]} для ошибок валидации полей —
    это поведение DRF по умолчанию, мы его не ломаем, а лишь
    гарантируем, что оно применяется единообразно.
    """
    response = exception_handler(exc, context)
    return response