import os
import subprocess
import threading
import backend.logger as logger

log = logger.get_new_logger("audio_player")

_is_playing = False
_play_lock = threading.Lock()

def play_audio(file_path: str):
    """
    Plays an audio file asynchronously using native tools.
    On macOS, uses afplay.
    Blocks concurrent playback.
    """
    global _is_playing
    
    with _play_lock:
        if _is_playing:
            return
        _is_playing = True

    if not os.path.isfile(file_path):
        log.warning(f"Audio file not found: {file_path}")
        with _play_lock:
            _is_playing = False
        return
        
    def _play():
        global _is_playing
        try:
            # Using macOS native audio player
            subprocess.run(["afplay", file_path], check=True)
        except Exception as e:
            log.error(f"Error playing audio file {file_path}: {e}")
        finally:
            with _play_lock:
                _is_playing = False
            
    threading.Thread(target=_play, daemon=True).start()
