import pygame, math, sys, random
from collections import deque
from pygame.locals import *


########################################################
# 1) Генерация лабиринта
########################################################
def generate_maze(width, height):
    maze = [list("#" * width) for _ in range(height)]
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    maze[start_y][start_x] = ' '
    stack = [(start_x, start_y)]
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == "#":
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[y + dy // 2][x + dx // 2] = ' '
            maze[ny][nx] = ' '
            stack.append((nx, ny))
        else:
            stack.pop()
    # Добавим ветвистости
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == "#" and random.random() < 0.05:
                passages = sum(maze[y + dy][x + dx] == ' ' for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)])
                if passages >= 2:
                    maze[y][x] = ' '
    # Сглаживание
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == "#":
                passages = sum(maze[y + dy][x + dx] == ' ' for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)])
                if passages >= 3:
                    maze[y][x] = ' '
    # Факелы
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if maze[y][x] == "#" and any(maze[y + dy][x + dx] == ' ' for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]):
                if random.random() < 0.1:
                    maze[y][x] = 'T'
    return ["".join(row) for row in maze]


########################################################
# 2) BFS освещение
########################################################
def build_lightmap(maze):
    h = len(maze)
    w = len(maze[0])
    lightmap = [[(0.0, 0.0, 0.0) for _ in range(w)] for __ in range(h)]
    torches = []
    for y in range(h):
        for x in range(w):
            if maze[y][x] == 'T':
                torches.append((x, y))
    TORCH_COLOR = (255.0, 150.0, 0.0)
    DECAY = 0.1
    from collections import deque
    queue = deque()
    for tx, ty in torches:
        visited = [[False] * w for _ in range(h)]
        queue.clear()
        queue.append((tx, ty, 1.0))
        visited[ty][tx] = True
        while queue:
            cx, cy, br = queue.popleft()
            r0, g0, b0 = lightmap[cy][cx]
            lightmap[cy][cx] = (r0 + TORCH_COLOR[0] * br,
                                g0 + TORCH_COLOR[1] * br,
                                b0 + TORCH_COLOR[2] * br)
            nbr = br - DECAY
            if nbr <= 0.01:
                continue
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if maze[ny][nx] == '#':
                        continue
                    if not visited[ny][nx]:
                        visited[ny][nx] = True
                        queue.append((nx, ny, nbr))
    return lightmap


########################################################
# 3) Управление
########################################################
def update_player(px, py, angle, keys, maze, move_speed):
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


########################################################
# 4) DDA
########################################################
def cast_ray_dda(px, py, angle, maze, w, h, max_dist=50.0):
    mapX = int(px)
    mapY = int(py)
    rayDirX = math.cos(angle)
    rayDirY = math.sin(angle)
    deltaDistX = abs(1.0 / rayDirX) if abs(rayDirX) > 1e-9 else 1e30
    deltaDistY = abs(1.0 / rayDirY) if abs(rayDirY) > 1e-9 else 1e30

    if rayDirX < 0:
        stepX = -1
        sideDistX = (px - mapX) * deltaDistX
    else:
        stepX = 1
        sideDistX = (mapX + 1.0 - px) * deltaDistX
    if rayDirY < 0:
        stepY = -1
        sideDistY = (py - mapY) * deltaDistY
    else:
        stepY = 1
        sideDistY = (mapY + 1.0 - py) * deltaDistY

    max_sqr = max_dist * max_dist
    distance = 0.0
    side = 0

    while True:
        if sideDistX < sideDistY:
            sideDistX += deltaDistX
            mapX += stepX
            side = 0
        else:
            sideDistY += deltaDistY
            mapY += stepY
            side = 1
        if mapX < 0 or mapX >= w or mapY < 0 or mapY >= h:
            return (distance, None, mapX, mapY, side)
        if side == 0:
            distance = abs((mapX - px + (1 - stepX) / 2) / rayDirX)
        else:
            distance = abs((mapY - py + (1 - stepY) / 2) / rayDirY)
        if distance * distance > max_sqr:
            return (distance, None, mapX, mapY, side)

        cell = maze[mapY][mapX]
        if cell == '#' or cell == 'T':
            return (distance, cell, mapX, mapY, side)


########################################################
# 5) Рендер (упрощённо)
########################################################
def render_frame(px, py, angle, maze, w, h, scr_w, scr_h, fov, lightmap, camOffset=0):
    """
    camOffset сдвигает горизонт.
    Если camOffset > 0, горизонт будет ниже (камера «выше»).
    Если camOffset < 0, горизонт будет выше (камера «опущена»).
    """
    frame = [[(' ', (0, 0, 0)) for _ in range(scr_w)] for _ in range(scr_h)]
    max_dist_wall = 20.0

    # Где находится горизонтальная линия
    horizonRow = scr_h // 2 + camOffset

    # floorSymbols
    floorSymbols = " .':;~"

    for col in range(scr_w):
        ray_angle = angle - fov / 2 + (col / scr_w) * fov
        dist, ctype, mapx, mapy, side = cast_ray_dda(px, py, ray_angle, maze, w, h)
        if dist is None:
            dist = 9999
        dist_corrected = dist * math.cos(ray_angle - angle)
        # высота столбца
        colHeight = int(scr_h / (dist_corrected + 0.0001))
        # top/bottom
        top = horizonRow - colHeight // 2
        bottom = top + colHeight

        # Ослабление по расстоянию
        fade = max(0, 1 - dist_corrected / max_dist_wall)

        # Lightmap
        if 0 <= mapx < w and 0 <= mapy < h:
            lr, lg, lb = lightmap[mapy][mapx]
        else:
            lr, lg, lb = 0, 0, 0

        # Цвет стены (упрощённо)
        baseGray = 120
        if ctype == 'T':
            baseGray = 200  # чуть ярче
        r_ = min(255, int(baseGray * fade + lr * 0.5 * fade))
        g_ = min(255, int(baseGray * fade + lg * 0.5 * fade))
        b_ = min(255, int(baseGray * fade + lb * 0.5 * fade))
        wallColor = (r_, g_, b_)

        for row in range(scr_h):
            if row < top:
                # Небо
                frame[row][col] = (' ', (20, 20, 60))
            elif top <= row < bottom and ctype is not None:
                # Стена/факел
                # Для упрощения рисуем один символ, напр. '#'
                # Если это факел, можно рисовать '&'
                if ctype == 'T':
                    ch = '&'
                else:
                    ch = '#'
                frame[row][col] = (ch, wallColor)
            else:
                # Пол
                # Чем дальше row от horizonRow, тем больше расстояние
                dy = row - horizonRow
                if dy <= 0:
                    # Над горизонтом -> тоже «небо»
                    frame[row][col] = (' ', (20, 20, 60))
                else:
                    distFloor = 0.3 * dy  # упрощённая формула (чем больше dy, тем дальше)
                    fadeFloor = max(0, 1 - distFloor / 15.0)
                    # Вычислим координаты?
                    # Для упрощения просто берем (mapx,mapy) => не совсем корректно
                    # Но хотя бы будет видно, что пол подсвечен
                    base_r, base_g, base_b = 30, 50, 30
                    rF = min(255, int(base_r + lr * 0.5 * fadeFloor))
                    gF = min(255, int(base_g + lg * 0.5 * fadeFloor))
                    bF = min(255, int(base_b + lb * 0.5 * fadeFloor))
                    idx = int((1.0 - fadeFloor) * (len(floorSymbols) - 1))
                    idx = max(0, min(idx, len(floorSymbols) - 1))
                    floorChar = floorSymbols[idx]
                    frame[row][col] = (floorChar, (rF, gF, bF))
    return frame


########################################################
# 6) Основной цикл
########################################################
def main():
    # Генерируем лабиринт
    maze_w = 101
    maze_h = 61
    maze = generate_maze(maze_w, maze_h)
    lightmap = build_lightmap(maze)

    pygame.init()
    # Увеличим окно
    screen = pygame.display.set_mode((2200, 1280))
    pygame.display.set_caption("Adjustable horizon, bigger font")
    clock = pygame.time.Clock()
    # font.size=24
    font = pygame.font.SysFont("Courier", 24)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Параметры игрока
    player_x = 3.5
    player_y = 3.5
    player_angle = 0.0

    # Увеличим ASCII‑разрешение
    scr_w = 440
    scr_h = 240
    fov = math.pi / 2

    # camOffset отвечает за то, где будет «горизонт»
    # Положительное значение camOffset сдвигает горизонт вниз
    # Отрицательное — вверх
    camOffset = 0

    while True:
        dt = clock.tick(30) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Для наглядности: стрелками вверх/вниз меняем camOffset
                if event.key == pygame.K_UP:
                    camOffset -= 5
                elif event.key == pygame.K_DOWN:
                    camOffset += 5

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        move_speed = 3.0 * dt
        player_x, player_y = update_player(player_x, player_y, player_angle, keys, maze, move_speed)

        mx, _ = pygame.mouse.get_rel()
        player_angle += mx * 0.005

        frame = render_frame(player_x, player_y, player_angle,
                             maze, maze_w, maze_h,
                             scr_w, scr_h, fov, lightmap,
                             camOffset=camOffset)

        screen.fill((0, 0, 0))
        cw, ch = font.size("A")
        for row in range(scr_h):
            for col in range(scr_w):
                c, color = frame[row][col]
                surf = font.render(c, True, color)
                screen.blit(surf, (col * cw, row * ch))
        pygame.display.flip()


if __name__ == "__main__":
    main()
