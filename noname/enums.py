import enum


class GameState(enum.Enum):
    MAIN_MENU = enum.auto()
    GAMEPLAY = enum.auto()
    PAUSE = enum.auto()
