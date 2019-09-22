import time
import song_light_data
import json
import codecs
import os

with codecs.open("settings.json", "r", "utf-8") as sfile:
    settings = json.loads(sfile.read())
DATA_FOLDER = os.path.join(os.getcwd(), settings['song_data_folder'])

META_MAP = {}
FALLBACK_MAP = {}
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
        if smeta.is_fallback:
            FALLBACK_MAP[smeta.artist] = fullpath

current_song_data = None
current_song_info = None
jump_time = -1
current_time = 0

FUNCTION_MAP = {}
SONG_RESET_FUNCTIONS = []
SONG_STOP_FUNCTIONS = []

COMMAND_DELAY = int(settings['command_delay'])


def run_command(cmd, args):
    if cmd in FUNCTION_MAP:
        func = FUNCTION_MAP[cmd]
        if func != None:
            print(f"Running command {cmd} with args {args}")
            func(current_song_data, current_song_info, args)
    else:
        print(f"Unknown command: \"{cmd}\" ran with args {args}")


def run_last(current_time):
    if current_song_data != None:
        events = current_song_data.events
        effective_time = current_time

        def filter_events(event):
            time, cmd, args = event
            return time * 1000 < effective_time
        to_run = list(filter(filter_events, events))
        to_run.sort(key=lambda x: x[0])
        if len(to_run) > 0:
            time, cmd, args = to_run.pop()
            run_command(cmd, args)


def on_song_change(song):
    global current_song_data, current_song_info, jump_time, current_time
    current_song_data = None
    current_song_info = song
    jump_time = -1
    current_time = 0
    if (song == None):
        print("Stopping")
        for func in SONG_STOP_FUNCTIONS:
            func()
        return

    print("Song Change", song)
    album = song['album']
    title = song['title']
    if album in META_MAP:
        if title in META_MAP[album]:
            data_file = META_MAP[album][title]
            print("Song file found:", data_file)
            current_song_data = song_light_data.parse_file(data_file)
    if current_song_data == None:
        # try fallback
        artist = song['artist']
        if artist in FALLBACK_MAP:
            data_file = FALLBACK_MAP[artist]
            print("Falling back to file:", data_file)
            current_song_data = song_light_data.parse_file(data_file)
    for func in SONG_RESET_FUNCTIONS:
        func(current_song_data, current_song_info)


def on_time_change(current):
    global current_time
    delta = current - current_time
    current_time = current
    if current_song_data != None:
        if (delta < 0):
            run_last(current)
        events = current_song_data.events
        effective_time = current + COMMAND_DELAY
        if jump_time > 0:
            effective_time -= jump_time

        def filter_events(event):
            time, cmd, args = event
            return time * 1000 > effective_time - delta and time * 1000 <= effective_time
        to_run = list(filter(filter_events, events))
        to_run.sort(key=lambda x: x[0])
        for ev in to_run:
            time, cmd, args = ev
            run_command(cmd, args)


def on_play_pause(playing, current_time):
    print("Playing" if playing else "Paused")
    if playing:
        run_last(current_time)


def song_function(*args, **kwargs):
    def decorator(func):
        FUNCTION_MAP[args[0].upper()] = func
        return func
    return decorator


def song_reset(func):
    SONG_RESET_FUNCTIONS.append(func)
    return func


def song_stop(func):
    SONG_STOP_FUNCTIONS.append(func)
    return func


@song_function("PRINT")
def print_func(data, info, args):
    print_string = " ".join(args)
    print(f"Song function: {print_string}")


@song_function("JUMP")
def jump_func(data, info, args):
    global jump_time
    jump_target = 0 if len(args) < 1 else int(args[0])
    jump_time = current_time - jump_target
    print(f"Jumping to {jump_target}, back {jump_time}")
