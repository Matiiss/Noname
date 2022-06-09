import os

import pygame

cwd = os.path.join(os.getcwd(), "assets")

input_dir = input("Input directory for images to be packed (in assets): ")
images = os.listdir(os.path.join(cwd, input_dir))

output_path = input("Output path for the spritesheet (in assets): ")
tile_size = int(input("Tile size (a single integer): "))


base_surf = pygame.Surface((len(images) * tile_size, tile_size), flags=pygame.SRCALPHA)
for col, image_name in enumerate(images):
    image = pygame.image.load(os.path.join(cwd, input_dir, image_name))
    base_surf.blit(image, (col * tile_size, 0))

pygame.image.save(base_surf, os.path.join(cwd, output_path))
