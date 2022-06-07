import esper

from .components import *


class MovementProcessor(esper.Processor):
    priority = 10

    def process(self, events: list, actual_frames: float) -> None:
        for entity, (pos, velocity) in self.world.get_components(Position, Velocity):
            pos += velocity * actual_frames


class RenderProcessor(esper.Processor):
    priority = 0

    def process(self, events: list, actual_frames: float) -> None:
        screen = self.world.screen
        self.sprites(screen)

    def sprites(self, screen: pygame.Surface) -> None:
        for entity, (pos, sprite) in self.world.get_components(Position, Sprite):
            screen.blit(sprite.image, pos)


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
        for entity, (pos, velocity, rect, sprite) in self.world.get_components(
            Position, Velocity, Rectangle, Sprite
        ):
            rect.center = pos + pygame.Vector2(sprite.image.get_size()) / 2
            rect.width, rect.height = (
                pygame.Vector2(sprite.original_image.get_size()) * 0.7
            )
            horizontal = rect.move(velocity.x * 5, 0)
            vertical = rect.move(0, velocity.y * 5)
            for tile_id, tile in self.world.get_component(Tile):
                if tile.colliderect(horizontal):
                    velocity.x = 0
                if tile.colliderect(vertical):
                    velocity.y = 0


class LightingProcessor(esper.Processor):
    def process(self, events: list, actual_frames: float) -> None:
        position = self.world.component_for_entity(self.world.player, Position)
        # hmm


processors = [processor() for processor in esper.Processor.__subclasses__()]
