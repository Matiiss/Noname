import math

import dda

collision_map = [
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 0, 1]
]

print(dda.from_angle(32, 32, math.radians(180), collision_map, 16))
print(dda.from_angle_range(32, 32, math.radians(10), math.radians(80), math.radians(1), collision_map, 16))
