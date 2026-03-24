import pygame
import math
def update_player(px, py, angle, keys, maze, move_speed):
    """
    Обновление позиции игрока; игрок может проходить только по клеткам с ' ' (не может идти через '#' или 'T').
    """
    def is_free(x, y):
        if x < 0 or y < 0 or y >= len(maze) or x >= len(maze[0]):
            return False
        return (maze[int(y)][int(x)] == ' ')
    new_x, new_y = px, py
    if keys[pygame.K_w]:
        new_x += math.cos(angle) * move_speed
        new_y += math.sin(angle) * move_speed
    if keys[pygame.K_s]:
        new_x -= math.cos(angle) * move_speed
        new_y -= math.sin(angle) * move_speed
    if keys[pygame.K_a]:
        new_x += math.sin(angle) * move_speed
        new_y -= math.cos(angle) * move_speed
    if keys[pygame.K_d]:
        new_x -= math.sin(angle) * move_speed
        new_y += math.cos(angle) * move_speed
    if is_free(new_x, py):
        px = new_x
    if is_free(px, new_y):
        py = new_y
    return px, py
