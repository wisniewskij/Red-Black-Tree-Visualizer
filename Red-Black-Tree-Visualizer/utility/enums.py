from enum import Enum


class RbtColor(Enum):
    RED = False
    BLACK = True


class Color(Enum):
    WHITE = (200, 200, 200)
    BLACK = (41, 41, 40)
    OUTLINE_BLACK = (9, 9, 9)
    RED = (138, 21, 15)
    GREEN = (29, 46, 7)
    LIGHT_BLUE = (45, 111, 181)
    HIGHLIGHT_YELLOW = (222, 244, 64)


class Operation(Enum):
    HIGHLIGHT = 0
    INSERT = 1
    FOUND = 2
    DELETE = 3
    TRANSPLANT = 4
    ROTATE = 5
    BUNDLE = 6
    MOVE = 7
    CHANGE_COLOR = 8
    CHANGE_LEN = 9
