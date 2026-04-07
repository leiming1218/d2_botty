import random
import keyboard
import time
import numpy as np

from health_manager import get_panel_check_paused, set_panel_check_paused
from inventory.personal import inspect_items
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab, convert_abs_to_screen
from utils.custom_mouse import mouse
from char.warlock import Warlock
from logger import Logger
from config import Config
from utils.misc import wait
from pather import Location
from target_detect import get_visible_targets, TargetInfo, log_targets

class EchoLock(Warlock):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up EchoLock")
        super().__init__(*args, **kwargs)

    def cast_buffs(self, casting_delay: float):
        super().cast_buffs(casting_delay)
        if self._skill_hotkeys["hex_bane"]:
            keyboard.send(self._skill_hotkeys["hex_bane"])
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.2)
        if self._skill_hotkeys["eldritch_blast"]:
            keyboard.send(self._skill_hotkeys["eldritch_blast"])
            mouse.click(button="right")
            wait(self._cast_duration, self._cast_duration + 0.2)

    def _cast_echo_blast(self):
        n_move = (0, -10)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        if self._skill_hotkeys["ring_of_fire"]:
            keyboard.send(self._skill_hotkeys["ring_of_fire"])
            mouse.click(button="right")
            wait(Config().char["casting_frames"]*0.04)
        if self._skill_hotkeys["lethargy"]:
            keyboard.send(self._skill_hotkeys["lethargy"])
            mouse.click(button="right")
            wait(Config().char["casting_frames"]*0.04)
        n_move = (40, 30)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        keyboard.send(self._skill_hotkeys["echo_strike"])
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        n_move = (-40, -50)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        n_move = (-40, 30)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        n_move = (40, -50)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        mouse.click(button="right")

    def _tele_and_echo(self, abs_move: tuple[int, int]):
        wait(Config().char["casting_frames"]*0.02)
        pos_m = convert_abs_to_monitor(abs_move)
        mouse.move(*pos_m)
        wait(Config().char["casting_frames"]*0.02)
        keyboard.send(Config().char["teleport"])
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        self._cast_echo_blast()


    def kill_council(self) -> bool:
        if Config().char["teleport"]:
            self._cast_echo_blast()
            self._tele_and_echo((40, -10))
            self._tele_and_echo((0, -10))
            self._tele_and_echo((300, -275))
            self._tele_and_echo((-150, -90))
            self._tele_and_echo((150, 90))
            self._tele_and_echo((-150, -110))
            self._tele_and_echo((150, 90))
            self._tele_and_echo((-150, -110))
            self._tele_and_echo((150, 90))
            self._tele_and_echo((-200, 150))
            self._tele_and_echo((0, -10))
            self._tele_and_echo((0, -10))
            self._tele_and_echo((0, -10))
            wait(0.40)
            keyboard.send(Config().char["teleport"])
        return True
    
    def _echo_striking(self, cast_pos_abs: tuple[float, float], delay: tuple[float, float] = (0.2, 0.3), spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["echo_strike"]:
            keyboard.send(self._skill_hotkeys["echo_strike"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            pos_m = convert_abs_to_monitor((x, y))
            mouse.move(*pos_m, delay_factor=[0.3, 0.6])
            mouse.press(button="right")
            wait(delay[0], delay[1])
            mouse.release(button="right")
        keyboard.send(Config().char["stand_still"], do_press=False)


    
    def kill_eldritch(self) -> bool:
        eld_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eld_pos_abs[0] * 0.9, eld_pos_abs[1] * 0.9]

        #put monster firstly
        self._cast_deathmark(cast_pos_abs);

        for _ in range(int(Config().char["atk_len_eldritch"])):
            self._echo_striking(cast_pos_abs, spray=90)
     
        self._pather.traverse_nodes((Location.A5_ELDRITCH_SAFE_DIST, Location.A5_ELDRITCH_END), self, timeout=1.4, force_tp=True)

    
    def kill_shenk(self) -> bool:
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]

        #put monster firstly
        self._cast_deathmark(cast_pos_abs);
        for _ in range(int(Config().char["atk_len_shenk"] * 0.5)):
            self._echo_striking(cast_pos_abs, spray=90)

        for _ in range(int(Config().char["atk_len_shenk"])):
            self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
            self._echo_striking([0,0], spray=90)

        return True
    
    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]

        #put monster firstly
        self._cast_deathmark(cast_pos_abs);

        for _ in range(int(Config().char["atk_len_pindle"])):
            self._echo_striking(cast_pos_abs, spray=11)

        wait(self._cast_duration, self._cast_duration + 0.2)
        # Move to items
        self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.4,force_tp=True)
        return True
    

    def kill_council(self) -> bool:
        def clear_inside():
            self._pather.traverse_nodes_fixed([(875, 20)], self)
            for _ in range(2):
                self._echo_striking([0,0], spray=90)

        def clear_outside():
            self._pather.traverse_nodes_fixed([(430, 642)], self)
            for _ in range(2):
                self._echo_striking([0,0], spray=90)

        atk_len = int(Config().char["atk_len_trav"]* 0.5)
        for _ in range(atk_len):
            clear_inside()
            clear_outside()
            clear_inside()
            clear_outside()

        return True
