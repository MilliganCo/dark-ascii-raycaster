import pygame
import math
def render_minimap(surface, maze, player_x, player_y, player_angle, scale=4, pos=(10,10)):
    """
    Рисует миникарту в углу.
    scale - размер клетки миникарты (например, 4 пикселя).
    pos - верхний левый угол миникарты на экране.
    """
    rows = len(maze)
    cols = len(maze[0])
    # Для каждого пикселя миникарты рисуем прямоугольник
    for y in range(rows):
        for x in range(cols):
            cell = maze[y][x]
            color = (0,0,0)
            if cell == '#':
                color = (100,100,100)
            elif cell == 'T':
                color = (255,0,0)
            elif cell == ' ':
                color = (20,20,20)
            rect = pygame.Rect(pos[0] + x*scale, pos[1] + y*scale, scale, scale)
            pygame.draw.rect(surface, color, rect)
    # Рисуем игрока
    px = int(player_x * scale) + pos[0]
    py = int(player_y * scale) + pos[1]
    pygame.draw.circle(surface, (0,255,0), (px,py), scale//2)
    # Рисуем направление взгляда
    dx = int(math.cos(player_angle)*scale*2)
    dy = int(math.sin(player_angle)*scale*2)
    pygame.draw.line(surface, (0,255,0), (px,py), (px+dx, py+dy), 2)
