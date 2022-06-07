import esper
import pygame

from .components import Position, Sprite, Velocity, Rectangle, Tile
from .enums import GameState
from .processors import processors
from .utils.assets import load_map, load_sprites


class Game:
    FPS = 60
    WIDTH, HEIGHT = 320, 180
    _FRAME_CONSTANT = 60

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), flags=pygame.SCALED
        )
        self.clock = pygame.time.Clock()

        self.world = esper.World()
        self.world.screen = self.screen
        for processor in processors:
            self.world.add_processor(processor, priority=processor.priority)

        self.add_tiles("assets/maps/map1.json")
        self.player = self.world.create_entity(
            Position(pygame.Vector2(self.screen.get_size()) / 2),
            Velocity(),
            Sprite(load_sprites("assets/images/player/1.png")[0]),
            Rectangle(),
        )
        self.world.player = self.player

        self.running = True

    def run(self) -> None:
        while self.running:
            self.main()

    def main(self) -> None:
        dt = self.clock.tick(self.FPS)
        actual_frames = min(dt / 1000 * self._FRAME_CONSTANT, 3)
        self.screen.fill("black")

        pygame.display.set_caption(f"FPS: {self.clock.get_fps():.0f}")

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        self.world.process(events, actual_frames)

        pygame.display.update()

    @classmethod
    def set_state(cls, new_state: GameState) -> None:
        cls.game_state = new_state

    def __del__(self) -> None:
        pygame.quit()

    def add_tiles(self, path: str) -> None:
        for data, position in load_map(path):
            tile = data["tile"]
            components = (Sprite(tile), Position(position))
            if data["collision"]:
                components += (Tile(*position, *tile.get_size()),)
            self.world.create_entity(*components)
