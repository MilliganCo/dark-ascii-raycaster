# maze.py
import random

def generate_maze(width, height):
    maze = [list("#"*width) for _ in range(height)]
    start_x = random.randrange(1, width, 2)
    start_y = random.randrange(1, height, 2)
    maze[start_y][start_x] = ' '
    stack = [(start_x, start_y)]
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(2,0),(-2,0),(0,2),(0,-2)]:
            nx, ny = x+dx, y+dy
            if 0<nx<width-1 and 0<ny<height-1 and maze[ny][nx] == "#":
                neighbors.append((nx, ny, dx, dy))
        if neighbors:
            nx, ny, dx, dy = random.choice(neighbors)
            maze[y+dy//2][x+dx//2] = ' '
            maze[ny][nx] = ' '
            stack.append((nx, ny))
        else:
            stack.pop()
    # Доп ветвистости
    for y in range(1,height-1):
        for x in range(1,width-1):
            if maze[y][x] == "#" and random.random()<0.05:
                passages = sum(maze[y+dy][x+dx]==' ' for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
                if passages>=2:
                    maze[y][x] = ' '
    for y in range(1,height-1):
        for x in range(1,width-1):
            if maze[y][x] == "#":
                passages = sum(maze[y+dy][x+dx]==' ' for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
                if passages>=3:
                    maze[y][x] = ' '
    # Факелы – вместо 'T' делаем запись в torches
    torches = []
    for y in range(1,height-1):
        for x in range(1,width-1):
            if maze[y][x] == "#" and any(maze[y+dy][x+dx]==' ' for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]):
                if random.random()<0.1:
                    # факел — запомним координаты
                    torches.append((x,y))
                    # оставляем # в карте
    # Превращаем лабиринт в список строк
    mazeStrings = ["".join(row) for row in maze]
    return (mazeStrings, torches)
