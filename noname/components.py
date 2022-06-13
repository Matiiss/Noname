from .settings import *


class Position(pygame.Vector2):
    @property
    def cx(self) -> int:
        return int(self.x) // TILE_SIZE

    @property
    def cy(self) -> int:
        return int(self.y) // TILE_SIZE

    @property
    def xr(self) -> float:
        return (self.x - self.cx * TILE_SIZE) / TILE_SIZE

    @property
    def yr(self) -> float:
        return (self.y - self.cy * TILE_SIZE) / TILE_SIZE


class Velocity(pygame.Vector2):
    pass


class Sprite:
    def __init__(self, image: pygame.Surface):
        self.image = image
        self.original_image = self.image


class Rectangle(pygame.Rect):
    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
        super().__init__(x, y, width, height)


class Tile(pygame.Rect):
    pass


class FRect:
    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0):
        self.x, self.y = x, y
        self.width, self.height = width, height

    def move(self, x_change, y_change):
        return FRect(self.x + x_change, self.y + y_change, self.width, self.height)

    def colliderect(self, other):
        return (
            self.x < other.x + other.width
            and self.x + self.width > other.x
            and self.y < other.y + other.height
            and self.y + self.height > other.y
        )

    @property
    def center(self):
        return self.x + self.width / 2, self.y + self.height / 2

    @center.setter
    def center(self, value: tuple[int, int] | pygame.Vector2):
        x, y = value
        self.x = x - self.width / 2
        self.y = y - self.height / 2

    def __str__(self):
        return f"<{self.__class__.__name__}({self.x, self.y, self.width, self.height})>"


class Line:
    def __init__(self, start=pygame.Vector2(0, 0), end=pygame.Vector2(0, 0)):
        self.start = start
        self.end = end
