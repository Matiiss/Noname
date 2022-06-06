from dataclasses import dataclass
from functools import lru_cache

import pygame


class Position(pygame.Vector2):
    pass


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
