
import os
import json
import time
import codecs
import song_service
import light_functions
import magichome

API_PATH = os.path.join(os.getenv(
    'APPDATA'), "Google Play Music Desktop Player/json_store/playback.json")


song = None
playing = True
last_time = 0


def update(json_data):
    global song, playing, last_time
    current = json_data['time']['current']
    if (playing != json_data['playing']):
        playing = json_data['playing']
        song_service.on_play_pause(playing, current)
        if (not playing):
            if (json_data['song']['title'] == None):
                song = json_data['song']
                song_service.on_song_change(None)
                return
    if song != json_data['song']:
        song = json_data['song']
        data = song.copy()
        data['length'] = json_data['time']['total']
        song_service.on_song_change(data)
        last_time = 0
    delta = current - last_time
    if (delta != 0):
        song_service.on_time_change(current)
    last_time = current


run_monitor = True


def start_monitor(sleep=0.05):
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
    light_functions.add_device(magichome.Device("10.0.0.20"))
    start_monitor()
