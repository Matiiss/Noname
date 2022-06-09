import json

import pygame


def load_sprites(
    path: str, size: int = 16, convert_alpha: bool = True
) -> list[pygame.Surface]:
    """Loads sprites from a sprite sheet in chunks of specified size, returns a list of sprite surfaces."""

    sheet = pygame.image.load(path)
    sw, sh = sheet.get_size()
    surfaces = [
        sheet.subsurface((x, y, size, size))
        for y in range(0, sh, size)
        for x in range(0, sw, size)
    ]
    if convert_alpha:
        return [surface.convert_alpha() for surface in surfaces]
    return surfaces


def load_map(
    path: str,
    mapping: dict[str, dict] | None = None,
) -> list[list[dict]]:
    """Returns an iterator that yields a tuple of tile data and its position."""

    if mapping is None:
        tiles = load_sprites("assets/images/tiles/sheet.png")
        mapping = {
            ".": {"tile": tiles[1], "collision": False},
            "x": {"tile": tiles[2], "collision": True},
        }
    with open(path, "r") as file:
        data = json.load(file)
    map_data = data["map"]
    return [[mapping[col] for col in row.replace(" ", "")] for row in map_data]
