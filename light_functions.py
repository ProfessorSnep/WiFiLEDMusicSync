
import time
from song_service import song_function, song_reset, song_stop
from magichome import CustomPresets as presets

home_devices = []


@song_function("FADE")
def set_fade(data, info, args):
    speed = int(args[0])
    color1, color2 = get_two_colors_from_args(data, args[1:7])
    for d in home_devices:
        d.set_custom(presets.create(presets.GRADUAL, speed, color1, color2))


@song_function("PULSE")
def set_pulse(data, info, args):
    speed = int(args[0])
    color1, color2 = get_two_colors_from_args(data, args[1:7])
    for d in home_devices:
        d.set_custom(presets.create(
            presets.FADE_FLOW_START_TO_END, speed, color1, color2))


@song_function("FLASH")
def set_flash(data, info, args):
    speed = int(args[0])
    color1, color2 = get_two_colors_from_args(data, args[1:7])
    for d in home_devices:
        d.set_custom(presets.create(
            presets.RUN_TWO_ALT_FADE_START_TO_END, speed, color1, color2))


@song_function("BLINK")
def set_blink(data, info, args):
    speed = int(args[0])
    color1, color2 = get_two_colors_from_args(data, args[1:7])
    for d in home_devices:
        d.set_custom(presets.create(
            presets.RUN_TWO_ALT_START_TO_END, speed, color1, color2))


@song_function("STROBE")
def strobe(data, info, args):
    speed = int(args[0])
    color1, color2 = get_two_colors_from_args(data, args[1:7])
    for d in home_devices:
        d.set_custom(presets.create(presets.STROBE, speed, color1, color2))


@song_function("SET")
def set_color(data, info, args):
    color = get_color_from_args(data, args)
    if color == (0, 0, 0):
        color = (0, 0, 1)
    for d in home_devices:
        d.set_color(*color)


@song_reset
def reset(data, info):
    for d in home_devices:
        d.turn_on()
        d.set_color(0, 0, 1)
    time.sleep(0.3)
    for d in home_devices:
        d.set_color(0, 0, 1)


@song_stop
def stop():
    for d in home_devices:
        d.turn_off()


def add_device(device):
    home_devices.append(device)


def get_color_from_args(data, args):
    color = args[:3]
    if len(color) == 1:
        return data.get_variable(color.pop())
    elif len(color) == 3:
        return tuple(map(int, color))
    print(f"Invalid color: {color}")


def get_two_colors_from_args(data, args):
    colors = args[:6]
    if len(args) == 2:
        arg1, arg2 = colors
        return get_color_from_args(data, [arg1]), get_color_from_args(data, [arg2])
    if len(args) == 4:
        try:
            int(colors[0])
            return get_color_from_args(data, colors[0:3]), get_color_from_args(data, [colors[3]])
        except:
            return get_color_from_args(data, [colors[0]]), get_color_from_args(data, colors[1:4])
    elif len(args) == 6:
        color1 = args[:3]
        color2 = args[3:6]
        return get_color_from_args(data, color1), get_color_from_args(data, color2)
    print(f"Invalid colors: {colors}")
