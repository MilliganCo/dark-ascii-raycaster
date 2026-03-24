import pygame, math, sys
from maze import generate_maze
from lighting import build_lightmap
from player import update_player
from render import final_render_with_sprites
from minimap import render_minimap

def main():
    # Генерируем лабиринт и получаем позиции факелов
    maze_w = 101
    maze_h = 61

    # Сейчас generate_maze возвращает (mazeStrings, torches_positions)
    mazeStrings, torches_positions = generate_maze(maze_w, maze_h)

    # Освещение
    # Если build_lightmap теперь тоже требует torches_positions, сделаем так:
    lightmap = build_lightmap(mazeStrings, torches_positions)

    pygame.init()
    # Большое окно
    screen = pygame.display.set_mode((2200, 1280))
    pygame.display.set_caption("Optimized ASCII Raycaster with Minimap")
    clock = pygame.time.Clock()

    # Увеличенный шрифт
    font = pygame.font.SysFont("Courier", 24)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Параметры игрока
    player_x = 3.5
    player_y = 3.5
    player_angle = 0.0

    # ASCII-разрешение (больше чем ранее)
    scr_w = 440
    scr_h = 240
    fov = math.pi / 2   # угол обзора ~90°
    camOffset = 0
    fogDistance = 30.0

    while True:
        dt = clock.tick(60) / 1000.0  # 60 FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # Управление camOffset по стрелкам
                if event.key == pygame.K_UP:
                    camOffset -= 5
                elif event.key == pygame.K_DOWN:
                    camOffset += 5

        # Выход по ESC
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        # Движение игрока
        move_speed = 3.0 * dt
        player_x, player_y = update_player(player_x, player_y, player_angle,
                                           keys, mazeStrings, move_speed)

        # Поворот камеры мышью
        mx, _ = pygame.mouse.get_rel()
        player_angle += mx * 0.005

        # Рендер всего кадра (стены + пол + факелы)
        # final_render_with_sprites — функция, которая внутри себя
        # сначала вызывает render_frame, затем render_sprites.
        frame = final_render_with_sprites(
            player_x, player_y, player_angle,
            mazeStrings,      # сама карта
            maze_w, maze_h,   # размеры
            scr_w, scr_h,     # ASCII-разрешение
            fov,              # угол обзора
            lightmap,
            camOffset,
            fogDistance,
            torches_positions
        )

        # Отрисовка ASCII на экран
        screen.fill((0, 0, 0))
        cw, ch = font.size("A")
        for row in range(scr_h):
            for col in range(scr_w):
                c, color = frame[row][col]
                surf = font.render(c, True, color)
                screen.blit(surf, (col*cw, row*ch))

        # Отрисовка миникарты
        render_minimap(screen, mazeStrings,
                       player_x, player_y, player_angle,
                       scale=4,
                       pos=(screen.get_width() - maze_w*4 - 10, 10))

        pygame.display.flip()

if __name__ == "__main__":
    main()
