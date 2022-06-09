import time

import esper

from .components import *


class MovementProcessor(esper.Processor):
    priority = 10

    def process(self, events: list, actual_frames: float) -> None:
        for entity, (pos, velocity) in self.world.get_components(Position, Velocity):
            pos += velocity * actual_frames


class RenderProcessor(esper.Processor):
    priority = 0

    pygame.font.init()
    font = pygame.font.Font(None, 16)

    def process(self, events: list, actual_frames: float) -> None:
        screen = self.world.screen
        self.tiles(screen)
        self.sprites(screen)

    def sprites(self, screen: pygame.Surface) -> None:
        for entity, (pos, sprite) in self.world.get_components(Position, Sprite):
            screen.blit(sprite.image, pos)

    def tiles(self, screen: pygame.Surface) -> None:
        for surface, position in self.world.map:
            screen.blit(surface, position)


class InputProcessor(esper.Processor):
    right = pygame.Vector2(1, 0)
    priority = 15

    def process(self, events: list, actual_frames: float) -> None:
        dx, dy = 0, 0
        pos, velocity, sprite = (
            self.world.component_for_entity(self.world.player, component)
            for component in (Position, Velocity, Sprite)
        )
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_a]:
            dx -= 1

        velocity.x, velocity.y = dx, dy
        if velocity:
            velocity.normalize_ip()
        velocity *= 0.7

        center = pos + pygame.Vector2(sprite.image.get_size()) / 2
        angle = (mouse_pos - center).normalize().angle_to(self.right)
        sprite.image = pygame.transform.rotate(sprite.original_image, angle)
        pos.x, pos.y = center - pygame.Vector2(sprite.image.get_size()) / 2


class CollisionProcessor(esper.Processor):
    priority = 13

    def process(self, events: list, actual_frames: float) -> None:
        for entity, (pos, vel, rect, sprite) in self.world.get_components(
            Position, Velocity, FRect, Sprite
        ):
            center_pos = Position(pos + pygame.Vector2(sprite.image.get_size()) / 2)
            new_pos = Position(center_pos + vel)
            cx, cy = new_pos.cx, new_pos.cy

            rect.center = center_pos
            horizontal_projection = rect.move(vel.x, 0)
            vertical_projection = rect.move(0, vel.y)

            start = time.perf_counter()
            tiles = [
                pygame.Rect(cx * TILE_SIZE, cy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                for cx, cy in (
                    (cx - 1, cy - 1),
                    (cx, cy - 1),
                    (cx + 1, cy - 1),
                    (cx + 1, cy),
                    (cx + 1, cy + 1),
                    (cx, cy + 1),
                    (cx - 1, cy + 1),
                    (cx - 1, cy),
                )
                if self.collides(cx, cy)
            ]
            for tile in tiles:
                if horizontal_projection.colliderect(tile):
                    vel.x = 0
                if vertical_projection.colliderect(tile):
                    vel.y = 0

    def collides(self, cx: int, cy: int) -> bool:
        try:
            return self.world.collision_map[cy][cx]
        except IndexError:
            return True


class LightingProcessor(esper.Processor):
    def process(self, events: list, actual_frames: float) -> None:
        position = self.world.component_for_entity(self.world.player, Position)
        # hmm


processors = [processor() for processor in esper.Processor.__subclasses__()]
