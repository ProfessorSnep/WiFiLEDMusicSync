import gpmdp_monitor
import time
import song_light_data
import json
import codecs
import os

with codecs.open("settings.json", "r", "utf-8") as sfile:
    settings = json.loads(sfile.read())
DATA_FOLDER = os.path.join(os.getcwd(), settings['song_data_folder'])
LIGHT_IPS = settings['light_ips']

META_MAP = {}
data_files = os.listdir(DATA_FOLDER)
for df in data_files:
    fullpath = os.path.join(DATA_FOLDER, df)
    ext = os.path.splitext(fullpath)[1]
    if (ext == ".ssld"):
        smeta = song_light_data.parse_file(fullpath, meta=True)
        if smeta.album != None and smeta.title != None:
            if smeta.album not in META_MAP:
                META_MAP[smeta.album] = {}
            META_MAP[smeta.album][smeta.title] = fullpath

current_song_data = None
current_song_info = None


def run_command(cmd, args):
    # TODO add more functions!
    if (cmd == "PRINT"):
        print("Song function: {0}".format(" ".join(args)))
    else:
        print("Unknown command: \"{0}\" ran with args {1}".format(cmd, args))


def on_song_change(song):
    global current_song_data, current_song_info
    current_song_data = None
    current_song_info = song
    if (song == None):
        print("Stopping")
        return

    album = song['album']
    title = song['title']
    if album in META_MAP:
        if title in META_MAP[album]:
            data_file = META_MAP[album][title]
            print("Song file found:", data_file)
            current_song_data = song_light_data.parse_file(data_file)
            print(current_song_data.events)
    print("Song Change", song)


def on_time_change(current, delta):
    if (delta != current):
        if current_song_data != None:
            events = current_song_data.events

            def filter_events(event):
                time, cmd, args = event
                return time * 1000 > current - delta and time * 1000 <= current
            to_run = list(filter(filter_events, events))
            to_run.sort(key=lambda x: x[0])
            for ev in to_run:
                time, cmd, args = ev
                run_command(cmd, args)


def on_play_pause(playing):
    print("Playing" if playing else "Paused")


gpmdp_monitor.on_song_change(on_song_change)
gpmdp_monitor.on_time_change(on_time_change)
gpmdp_monitor.on_play_pause(on_play_pause)

# TODO flip this so the GPM monitor is the service
# handle events in the GPM service, call this service directly

if __name__ == "__main__":
    gpmdp_monitor.start_monitor()
