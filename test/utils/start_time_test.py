from datetime import datetime, time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from utils.start_time import is_bot_start_time_allowed


@pytest.mark.parametrize(
    "current_time, expected",
    [
        (time(6, 59, 59), False),
        (time(7, 0), True),
        (time(22, 59, 59), True),
        (time(23, 0), False),
    ],
)
def test_bot_start_time_window(current_time: time, expected: bool):
    assert is_bot_start_time_allowed(current_time) is expected


def test_bot_exits_after_game_when_start_window_is_closed(monkeypatch, capsys):
    import bot as bot_module

    class ExitRequested(Exception):
        pass

    now = datetime(2026, 11, 13, 23, 0)
    config = SimpleNamespace(
        general={
            "info_screenshots": False,
            "max_runtime_before_break_m": 0,
            "break_length_m": 0,
            "randomize_runs": False,
        }
    )
    monkeypatch.setattr(bot_module, "Config", lambda: config)
    monkeypatch.setattr(bot_module, "datetime", SimpleNamespace(now=lambda: now))
    monkeypatch.setattr(bot_module, "is_bot_start_time_allowed", lambda _: False)
    monkeypatch.setattr(bot_module, "view", SimpleNamespace(save_and_exit=lambda: True))
    monkeypatch.setattr(bot_module, "set_pause_state", lambda _: None)
    monkeypatch.setattr(bot_module, "restore_d2r_window_visibility", Mock())
    monkeypatch.setattr(bot_module.Logger, "info", lambda _: None)

    def exit_process(exit_code: int):
        raise ExitRequested(exit_code)

    monkeypatch.setattr(bot_module.os, "_exit", exit_process)

    bot = bot_module.Bot.__new__(bot_module.Bot)
    bot._game_stats = Mock()
    bot._curr_loc = None
    bot._pre_buffed = False
    bot._do_runs = {"run": True}
    bot._do_runs_reset = {"run": True}
    bot._timer = bot_module.time.time()
    bot._messenger = SimpleNamespace(enabled=False)
    bot.trigger_or_stop = Mock()

    with pytest.raises(ExitRequested) as exit_request:
        bot.on_end_game()

    assert exit_request.value.args == (0,)
    bot._game_stats.log_end_game.assert_called_once_with(failed=False)
    bot.trigger_or_stop.assert_not_called()
    bot_module.restore_d2r_window_visibility.assert_called_once_with()
    assert "Bot stopping after this game" in capsys.readouterr().out


def test_configured_break_randomizes_duration_by_twenty_percent(monkeypatch):
    import bot as bot_module

    now = datetime(2026, 11, 13, 22, 0)
    config = SimpleNamespace(
        general={
            "info_screenshots": False,
            "max_runtime_before_break_m": 60,
            "break_length_m": 25,
            "randomize_runs": False,
        }
    )
    monkeypatch.setattr(bot_module, "Config", lambda: config)
    monkeypatch.setattr(bot_module, "datetime", SimpleNamespace(now=lambda: now))
    monkeypatch.setattr(bot_module, "is_bot_start_time_allowed", lambda _: True)
    monkeypatch.setattr(bot_module, "view", SimpleNamespace(save_and_exit=lambda: True))
    monkeypatch.setattr(bot_module, "set_pause_state", lambda _: None)
    monkeypatch.setattr(bot_module.Logger, "info", lambda _: None)
    monkeypatch.setattr(bot_module.Logger, "debug", lambda _: None)
    timestamps = iter((3_601, 3_602))
    monkeypatch.setattr(bot_module.time, "time", lambda: next(timestamps))
    wait = Mock()
    monkeypatch.setattr(bot_module, "wait", wait)
    uniform = Mock(return_value=30)
    monkeypatch.setattr(bot_module.random, "uniform", uniform)

    bot = bot_module.Bot.__new__(bot_module.Bot)
    bot._game_stats = Mock()
    bot._curr_loc = None
    bot._pre_buffed = False
    bot._do_runs = {"run": True}
    bot._do_runs_reset = {"run": True}
    bot._timer = 0
    bot._messenger = SimpleNamespace(enabled=False)
    bot._pausing = False
    bot.toggle_pause = Mock(side_effect=lambda: setattr(bot, "_pausing", not bot._pausing))
    bot.trigger_or_stop = Mock()

    bot.on_end_game()

    uniform.assert_called_once_with(20, 30)
    wait.assert_called_once_with(30 * 60)
    assert bot._timer == 3_602
    assert bot.toggle_pause.call_count == 2
    bot.trigger_or_stop.assert_called_once_with("init")
