"""MPRIS media controller via D-Bus."""
import dbus


def _get_player():
    try:
        bus = dbus.SessionBus()
        names = [
            n for n in bus.list_names()
            if str(n).startswith("org.mpris.MediaPlayer2.")
        ]
        if not names:
            return None, None
        # Prefer non-browser-integration if available
        preferred = [n for n in names if "plasma-browser-integration" not in str(n)]
        name = preferred[0] if preferred else names[0]
        proxy = bus.get_object(name, "/org/mpris/MediaPlayer2")
        return proxy, name
    except Exception:
        return None, None


def get_media_info():
    proxy, name = _get_player()
    if proxy is None:
        return {"status": "none", "artist": "", "title": "", "app": ""}

    try:
        props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
        meta = props.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        status = str(props.Get("org.mpris.MediaPlayer2.Player", "PlaybackStatus"))

        artist_list = meta.get("xesam:artist", [])
        artist = str(artist_list[0]) if artist_list else ""
        title = str(meta.get("xesam:title", ""))
        app_name = str(name).replace("org.mpris.MediaPlayer2.", "").split(".")[0].capitalize()

        return {
            "status": status.lower(),
            "artist": artist,
            "title": title,
            "app": app_name,
        }
    except Exception:
        return {"status": "none", "artist": "", "title": "", "app": ""}


def _player_cmd(method_name):
    proxy, _ = _get_player()
    if proxy is None:
        return
    try:
        iface = dbus.Interface(proxy, "org.mpris.MediaPlayer2.Player")
        getattr(iface, method_name)()
    except Exception:
        pass


def play_pause():
    _player_cmd("PlayPause")


def next_track():
    _player_cmd("Next")


def prev_track():
    _player_cmd("Previous")
