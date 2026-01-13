import logging
from functools import wraps
from datetime import datetime


def log_action(action_name=None, verbose=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)

            action = action_name or func.__name__.upper()

            log_context = {
                "action": action,
                "timestamp": datetime.now().isoformat()
            }

            try:
                result = func(*args, **kwargs)

                # логируем успех
                if result and isinstance(result, dict):
                    log_context.update({
                        "result": "OK",
                        "username": result.get("username"),
                        "user_id": result.get("user_id"),
                        "currency_code": result.get("currency"),
                        "amount": result.get("amount"),
                        "rate": result.get("rate"),
                        "base": result.get("base_currency", "USD")
                    })

                if verbose:
                    log_context["verbose"] = True

                # формируем сообщение
                msg_parts = [f"{log_context['action']}"]
                for key in ["username", "user_id", "currency_code", "amount", "rate"]:
                    if key in log_context and log_context[key] is not None:
                        msg_parts.append(f"{key}='{log_context[key]}'")

                logger.info(" ".join(msg_parts))

                return result

            except Exception as e:
                # Логируем ошибку
                log_context.update({
                    "result": "ERROR",
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                })

                logger.error(
                    f"{log_context['action']} "
                    f"error_type='{log_context['error_type']}' "
                    f"error='{log_context['error_message']}'"
                )

                # пробрасываем исключение дальше
                raise

        return wrapper

    return decorator
