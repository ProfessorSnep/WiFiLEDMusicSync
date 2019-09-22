import codecs

GLOBAL_VARIABLES = {"RED": (255, 0, 0), "GREEN": (
    0, 255, 0), "BLUE": (0, 0, 255), "CYAN": (0, 255, 255),
    "MAGENTA": (255, 0, 255), "YELLOW": (255, 255, 0), "ORANGE": (255, 30, 0)}


class SongData:
    def __init__(self):
        self.title = None
        self.album = None
        self.events = []
        self.variables = {}

    def get_variable(self, var):
        var = var.upper()
        if var in self.variables:
            return self.variables[var]
        if var in GLOBAL_VARIABLES:
            return GLOBAL_VARIABLES[var]
        return None


def parse_meta(data, line):
    if line.startswith("#"):
        tags = line.split(" ")
        head = tags[0][1:]
        body = " ".join(tags[1:])
        if head.upper() == "ALBUM":
            data.album = body
        elif head.upper() == "TITLE":
            data.title = body


def parse_line(data, line):
    if line.startswith("//"):
        # COMMENT
        return None
    elif line.startswith("#"):
        # META TAGS
        parse_meta(data, line)
    else:
        # SONG DATA
        tags = line.split(" ")
        if (len(tags) > 1):
            if (tags[0].upper() == "COLOR"):
                name = tags[1].upper()
                args = tuple(map(int, tags[2:5]))
                data.variables[name] = args
            else:
                time = float(tags[0])
                cmd = tags[1].upper()
                args = tags[2:]
                data.events.append((time, cmd, args))
        else:
            # EMPTY LINE
            pass


def parse_lines(lines, meta=False):
    data = SongData()
    line_number = 0
    for line in lines:
        line_number += 1
        if (meta):
            parse_meta(data, line.rstrip())
        else:
            parse_line(data, line.rstrip())
    return data


def parse_file(file, meta=False):
    with codecs.open(file, "r", "utf-8") as filedata:
        return parse_lines(filedata.readlines(), meta=meta)
