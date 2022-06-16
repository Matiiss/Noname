import math

import dda
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

    camera = pygame.Vector2(0, 0)

    shadow_surface = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA)
    shadow_surface.set_colorkey("white")

    def process(self, events: list, actual_frames: float) -> None:
        screen = self.world.screen
        pos, sprite = [
            self.world.component_for_entity(self.world.player, component)
            for component in (Position, Sprite)
        ]
        self.get_offset(pos + pygame.Vector2(sprite.image.get_size()) / 2)
        self.tiles(screen, self.camera)
        self.draw_shadow(self.camera)
        self.sprites(screen, self.camera)

    def sprites(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        # TODO: fix blending with other entities when being on them

        surf = self.shadow_surface

        for entity, (pos, sprite) in self.world.get_components(Position, Sprite):
            final = pos + offset
            surf.blit(sprite.image, final, special_flags=pygame.BLEND_RGBA_MIN)

        screen.blit(surf, (0, 0))

    def tiles(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        for surface, position in self.world.map:
            final = position + offset
            screen.blit(surface, final)

    def get_offset(self, tracked_pos: pygame.Vector2) -> None:
        camera = pygame.Vector2((WIDTH, HEIGHT)) / 2 - tracked_pos
        self.camera = pygame.Vector2(round(camera.x), round(camera.y))

    def draw_lines(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        for entity, (line, *_) in self.world.get_components(Line):
            pygame.draw.line(screen, "white", line.start - offset, line.end - offset)

    def draw_shadow(self, offset: pygame.Vector2) -> None:
        surf = self.shadow_surface
        surf.fill((0, 0, 0, 70))
        pygame.draw.polygon(surf, "white", [point + offset for point in points])
        pygame.draw.circle(surf, "white", points[0] + offset, 15)
        # pygame.draw.aaline(surf, "white", points[0] + offset, points[1] + offset, blend=True)
        # pygame.draw.aaline(surf, "white", points[0] + offset, points[-1] + offset, blend=True)


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
        mouse_pos = (
            pygame.Vector2(pygame.mouse.get_pos())
            + pos
            + pygame.Vector2(sprite.image.get_size()) / 2
            - pygame.Vector2(self.world.screen.get_size()) / 2
        )

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
        global angle
        angle = (
            ((mouse_pos - center) or pygame.Vector2(1, 0))
            .normalize()
            .angle_to(self.right)
        )
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
            if not tiles:
                return

            rect.center = center_pos
            horizontal_projection = rect.move(vel.x, 0)
            vertical_projection = rect.move(0, vel.y)

            for tile in tiles:
                if horizontal_projection.colliderect(tile):
                    vel.x = 0
                if vertical_projection.colliderect(tile):
                    vel.y = 0

    # @functools.lru_cache(maxsize=512)
    def collides(self, cx: int, cy: int) -> bool:
        map_ = self.world.collision_map
        if 0 <= cy < len(map_) and 0 <= cx < len(map_[0]):
            return map_[cy][cx]
        return True


class LightingProcessor(esper.Processor):
    priority = 5

    def process(self, events: list, actual_frames: float) -> None:
        global points
        points = []

        position = self.world.component_for_entity(self.world.player, Position)
        sprite = self.world.component_for_entity(self.world.player, Sprite)
        x, y = position = Position(
            position + pygame.Vector2(sprite.image.get_size()) / 2
        )
        collision_map = self.world.collision_map

        points.append(position)
        start, stop, step = (
            math.radians(angle - 45),
            math.radians(angle + 45),
            math.radians(0.5),
        )

        points.extend(
            dda.from_angle_range(
                x,
                y,
                start,
                stop,
                step,
                collision_map,
                TILE_SIZE,
            )
        )


processors = [processor() for processor in esper.Processor.__subclasses__()]
