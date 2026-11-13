from datetime import datetime, time


_BOT_START_TIME = time(7, 0)
_BOT_END_TIME = time(23, 0)


def is_bot_start_time_allowed(current_time: time | None = None) -> bool:
    if current_time is None:
        current_time = datetime.now().time()
    return _BOT_START_TIME <= current_time < _BOT_END_TIME
