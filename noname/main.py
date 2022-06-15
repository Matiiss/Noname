import esper

from .components import *
from .enums import GameState
from .processors import processors
from .settings import *
from .utils.assets import load_map, load_sprites


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=DISPLAY_FLAGS)
        self.clock = pygame.time.Clock()

        self.world = esper.World()
        self.world.screen = self.screen
        for processor in processors:
            self.world.add_processor(processor, priority=processor.priority)

        self.world.map, self.world.collision_map = self.load_tiles(
            "assets/maps/map1.json"
        )
        self.player = self.world.create_entity(
            Position(pygame.Vector2(self.screen.get_size()) / 2),
            Velocity(),
            Sprite(load_sprites("assets/images/player/1.png")[0]),
            FRect(width=10, height=10),
        )
        self.world.player = self.player

        self.running = True

        # self.world.lines = [self.world.create_entity(Line()) for _ in range(360)]

        green_square = pygame.Surface((50, 50))
        green_square.fill("green")
        for _ in range(10):
            self.world.create_entity(Position(0, 0), Sprite(green_square))

    def run(self) -> None:
        while self.running:
            self.main()

    def main(self) -> None:
        dt = self.clock.tick(FPS)
        actual_frames = min(dt / 1000 * FRAME_CONSTANT, 3)
        self.screen.fill("black")

        pygame.display.set_caption(f"FPS: {self.clock.get_fps():.0f}")

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # TODO: add fullscreen toggle (F11 to enter and ESC to exit fullscreen mode)
                    pass

        self.world.process(events, actual_frames)

        pygame.display.update()

    @classmethod
    def set_state(cls, new_state: GameState) -> None:
        cls.game_state = new_state

    def __del__(self) -> None:
        pygame.quit()

    @staticmethod
    def load_tiles(
        path: str,
    ) -> tuple[tuple[tuple[pygame.Surface, pygame.Vector2], ...], list[list[bool]],]:
        tile_array = load_map(path=path)
        return tuple(
            (data["tile"], pygame.Vector2(col * TILE_SIZE, row * TILE_SIZE))
            for row, row_data in enumerate(tile_array)
            for col, data in enumerate(row_data)
        ), list(list(data["collision"] for data in row) for row in tile_array)
