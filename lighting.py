# lighting.py
from collections import deque

def build_lightmap(maze, torches_positions):
    """
    Построение lightmap, где torches_positions — список (x,y) для факелов.
    maze[y][x] == '#' (стена). Разрешаем BFS проходить сквозь 1 слой стены?
    Или лучше: начнем BFS из соседних клеток ' ', если хотим.
    Здесь покажем упрощённо: BFS стартует прямо из (x,y),
    но если там '#', мы даём br=1.0 -> brWall=0.5 -> ...
    """
    h = len(maze)
    w = len(maze[0])
    lightmap = [[(0.0,0.0,0.0) for _ in range(w)] for __ in range(h)]
    TORCH_COLOR = (255.0, 150.0, 0.0)
    DECAY = 0.1

    for (fx, fy) in torches_positions:
        queue = deque()
        visited = [[False]*w for _ in range(h)]
        # Начальное br=1.0
        queue.append((fx, fy, 1.0))
        visited[fy][fx] = True
        while queue:
            cx, cy, br = queue.popleft()
            r0,g0,b0 = lightmap[cy][cx]
            lightmap[cy][cx] = (r0+TORCH_COLOR[0]*br,
                                g0+TORCH_COLOR[1]*br,
                                b0+TORCH_COLOR[2]*br)
            new_br = br - DECAY
            if new_br<=0.01:
                continue
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = cx+dx, cy+dy
                if 0<=nx<w and 0<=ny<h:
                    if visited[ny][nx]:
                        continue
                    cell = maze[ny][nx]
                    if cell=='#':
                        # Разрешаем 1 слой стены?
                        # Либо игнорируем, BFS не пойдёт за стену
                        continue
                    visited[ny][nx]=True
                    queue.append((nx, ny, new_br))
    return lightmap
