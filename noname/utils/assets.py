import json
import typing as t

import pygame


def load_sprites(
    path: str, size: tuple[int, int] = (16, 16), convert_alpha: bool = True
) -> list[pygame.Surface]:
    """Loads sprites from a sprite sheet in chunks of specified size, returns a list of sprite surfaces."""

    sheet = pygame.image.load(path)
    w, h, sw, sh = size + sheet.get_size()
    surfaces = [
        sheet.subsurface((x, y, *size))
        for y in range(0, sh, h)
        for x in range(0, sw, w)
    ]
    if convert_alpha:
        return [surface.convert_alpha() for surface in surfaces]
    return surfaces


def load_map(
    path: str,
    size: tuple[int, int] = (16, 16),
    mapping: dict[str, dict] | None = None,
) -> t.Generator[tuple[dict, tuple[int, int]], None, None]:
    """Returns an iterator that yields a tuple of tile data and its position."""

    width, height = size
    if mapping is None:
        tiles = load_sprites("assets/images/tiles/sheet.png", (16, 16))
        mapping = {
            ".": {"tile": tiles[1], "collision": False},
            "x": {"tile": tiles[2], "collision": True},
        }
    with open(path, "r") as file:
        data = json.load(file)
    map_data = data["map"]
    for row, row_data in enumerate(map_data):
        for col, col_data in enumerate(row_data.replace(" ", "")):
            yield mapping[col_data], (width * col, height * row)
