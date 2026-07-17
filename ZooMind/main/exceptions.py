from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    responce = exception_handler(exc, context)
    if responce is None:
        return responce

    status_code = responce.status_code
    original_data = responce.data

    if isinstance(original_data, dict):
        message = original_data.get("detail", "Ошибка запроса")
        errors = original_data
    else:
        message = "Ошибка запроса"
        errors = original_data

    if status_code == 400:
        message = "Ошибка валидации данных"
    elif status_code == 401:
        message = "Ошибка авторизации"
    elif status_code == 403:
        message = "Доступ запрещен"
    elif status_code == 404:
        message = "Объект не найден"
    elif status_code == 429:
        message = "Слишком много запросов"

    responce.data = {
        "success": False,
        "status_code": status_code,
        "message": message,
        "errors": errors,

    }
    return responce