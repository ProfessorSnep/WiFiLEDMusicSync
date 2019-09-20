
import os
import json
import time
import codecs

API_PATH = os.path.join(os.getenv(
    'APPDATA'), "Google Play Music Desktop Player/json_store/playback.json")


song = None
playing = True
last_time = 0


def update(json_data):
    global song, playing, last_time
    if (playing != json_data['playing']):
        playing = json_data['playing']
        fire_event(play_pause_callbacks, playing)
        if (not playing):
            if (json_data['song']['title'] == None):
                song = json_data['song']
                fire_event(song_change_callbacks, None)
                return
    if song != json_data['song']:
        song = json_data['song']
        data = song.copy()
        data['length'] = json_data['time']['total']
        fire_event(song_change_callbacks, data)
        last_time = 0
    current = json_data['time']['current']
    delta = current - last_time
    if (delta != 0):
        fire_event(time_change_callbacks, current, current - last_time)
    last_time = current


time_change_callbacks = []


def on_time_change(callback):
    """Register a callback for when the song progresses in time.

    Callback requires current(int), and delta(int)
    """
    global time_change_callbacks
    time_change_callbacks += [callback]


play_pause_callbacks = []


def on_play_pause(callback):
    """Register a callback for when the song starts or stops playing.

    Callback requires playing(bool)
    """
    global play_pause_callbacks
    play_pause_callbacks += [callback]


song_change_callbacks = []


def on_song_change(callback):
    """Register a callback for when the song changes.

    Callback requires song(map)
    """
    global song_change_callbacks
    song_change_callbacks += [callback]


def fire_event(callbacks, *args):
    for callback in callbacks:
        callback(*args)


run_monitor = True


def start_monitor(sleep=0.1):
    global run_monitor
    run_monitor = True
    with codecs.open(API_PATH, "r", "utf-8") as jf:
        while(run_monitor):
            try:
                jf.seek(0)
                c = jf.read()
                j = json.loads(c)

                update(j)

                time.sleep(sleep)
            except json.decoder.JSONDecodeError as e:
                pass

def stop_monitor():
    global run_monitor
    run_monitor = False


if __name__ == "__main__":
    start_monitor()
