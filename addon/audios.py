from pathlib import Path
from typing import Literal, Union

from aqt import mw, gui_hooks
from aqt.webview import AnkiWebView, WebContent
import aqt.sound
from aqt.sound import SoundOrVideoTag, AVPlayer

try:  # 2.1.50+
    from anki.utils import is_win
except:
    from anki.utils import isWin as is_win


class CustomAVPlayer(AVPlayer):
    no_interrupt = False

    def _on_play_without_interrupt_finished(self) -> None:
        self.no_interrupt = False
        self._on_play_finished()

    def _stop_if_playing(self) -> None:
        if self.current_player and not self.no_interrupt:
            self.current_player.stop()

    def play_without_interrupt(self, file: Path) -> None:
        """Audio played with this function will not be interrupted by other audio
        except audio played through this function.
        This function does not clear existing audio queue created by other play methods.
        """
        if self.current_player:
            self.current_player.stop()

        self.no_interrupt = True
        tag = SoundOrVideoTag(filename=str(file.resolve()))
        best_player = self._best_player_for_tag(tag)
        if best_player:
            self.current_player = best_player
            gui_hooks.av_player_will_play(tag)
            self.current_player.play(tag, self._on_play_without_interrupt_finished)
        else:
            print(f"ERROR: no players found for {tag}")


def will_use_audio_player() -> None:
    aqt.sound.av_player.no_interrupt = False
    AVPlayer._on_play_without_interrupt_finished = (
        CustomAVPlayer._on_play_without_interrupt_finished
    )
    AVPlayer._stop_if_playing = CustomAVPlayer._stop_if_playing  # type: ignore
    AVPlayer.play_without_interrupt = CustomAVPlayer.play_without_interrupt


def audio(file: Path) -> None:
    aqt.sound.av_player.play_without_interrupt(file)
