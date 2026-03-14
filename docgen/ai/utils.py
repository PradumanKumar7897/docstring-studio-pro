import time


def retry_with_backoff(func, retries):
    delay = 1
    for attempt in range(retries):
        try:
            return func()
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2