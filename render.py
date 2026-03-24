# render.py
import math

def cast_ray_dda(px, py, angle, maze, w, h, max_dist=50.0):
    """
    Классическая DDA-функция: возвращает (distance, cellType, mapX, mapY, side),
    где cellType — '#' или None, side — вертикальное/горизонтальное пересечение.
    """
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
        # Двигаемся либо по X, либо по Y
        if sideDistX < sideDistY:
            sideDistX += deltaDistX
            mapX += stepX
            side = 0
        else:
            sideDistY += deltaDistY
            mapY += stepY
            side = 1

        # Проверка выхода за пределы
        if mapX < 0 or mapX >= w or mapY < 0 or mapY >= h:
            return (distance, None, mapX, mapY, side)

        # Рассчитываем точное расстояние
        if side == 0:
            distance = abs((mapX - px + (1 - stepX) / 2) / (rayDirX + 1e-12))
        else:
            distance = abs((mapY - py + (1 - stepY) / 2) / (rayDirY + 1e-12))

        if distance * distance > max_sqr:
            return (distance, None, mapX, mapY, side)

        # Если наткнулись на стену (или 'T')
        cell = maze[mapY][mapX]
        if cell == '#' or cell == 'T':
            return (distance, cell, mapX, mapY, side)


def render_sprites(frame, px, py, angle, torches, scr_w, scr_h, fov):
    """
    Упрощённо вставляем ASCII-спрайт факела (&) в кадр,
    если факел попадает в поле зрения (fov) и находится ближе, чем стена.
    (Без учёта Z-буфера и реальных перекрытий стен.)
    """
    import math

    sprite_data = []
    for (fx, fy) in torches:
        dx = fx - px
        dy = fy - py
        distS = math.hypot(dx, dy)
        spriteAngle = math.atan2(dy, dx) - angle
        # нормализуем угол в [-pi, pi]
        spriteAngle = (spriteAngle + math.pi) % (2*math.pi) - math.pi
        sprite_data.append((distS, spriteAngle, fx, fy))

    # Сортируем (убывание), чтобы ближние перекрывали дальние
    sprite_data.sort(key=lambda x: x[0], reverse=True)

    halfFov = fov/2

    for (distS, sAng, fx, fy) in sprite_data:
        # Если угол за пределами fov, пропускаем
        if sAng < -halfFov or sAng > halfFov:
            continue
        # Находим столбец
        alpha = sAng / halfFov  # [-1..1]
        col = int((alpha + 1)/2 * scr_w)
        if distS < 0.0001:
            distS = 0.0001
        height = int(scr_h / distS)

        # Координаты спрайта (узкая колонка)
        top = scr_h // 2 - height//2
        bottom = top + height
        tch = '&'  # символ факела
        color = (255, 150, 0)

        for row in range(top, bottom):
            if 0 <= row < scr_h and 0 <= col < scr_w:
                # Здесь не проверяем, ближе ли спрайт, чем стена
                # (Упрощение!)
                frame[row][col] = (tch, color)


def render_frame(px, py, angle, maze, w, h, scr_w, scr_h, fov, lightmap,
                 camOffset=0, fogDistance=30.0):
    """
    Основной рендер (стены + пол) с классическим floor casting,
    где пол корректно уходит вдаль, а стены рисуются через DDA.
    """
    frame = [[(' ', (0, 0, 0)) for _ in range(scr_w)] for _ in range(scr_h)]

    horizonRow = scr_h // 2 + camOffset
    floorSymbols = " .':;~"

    # Для интерполяции направления пола (слева-направо)
    leftAngle = angle - fov / 2
    rightAngle = angle + fov / 2
    sinA0 = math.sin(leftAngle)
    cosA0 = math.cos(leftAngle)
    sinA1 = math.sin(rightAngle)
    cosA1 = math.cos(rightAngle)

    for col in range(scr_w):
        # 1) Трассировка луча DDA
        ray_angle = leftAngle + (col / (scr_w - 1))*(rightAngle - leftAngle)
        dist, ctype, mapx, mapy, side = cast_ray_dda(px, py, ray_angle, maze, w, h, max_dist=fogDistance)
        if dist is None:
            dist = 9999.0
        dist_corr = dist * math.cos(ray_angle - angle)

        colHeight = int(scr_h / (dist_corr + 0.0001))
        top = horizonRow - colHeight // 2
        bottom = top + colHeight

        # Туман (fog)
        fogFactor = 1.0
        if dist_corr > fogDistance:
            fogFactor = max(0.0, 1.0 - (dist_corr - fogDistance)/fogDistance)

        # Lightmap (для стены)
        lr, lg, lb = 0, 0, 0
        if mapx >= 0 and mapx < w and mapy >= 0 and mapy < h:
            lr, lg, lb = lightmap[mapy][mapx]

        baseGray = 120 if (ctype != 'T') else 200
        r_wall = min(255, int(baseGray*fogFactor + lr*0.5*fogFactor))
        g_wall = min(255, int(baseGray*fogFactor + lg*0.5*fogFactor))
        b_wall = min(255, int(baseGray*fogFactor + lb*0.5*fogFactor))
        wallColor = (r_wall, g_wall, b_wall)
        wallChar = '#' if (ctype != 'T') else '&'

        # Заполнение кадра
        for row in range(scr_h):
            if row < top:
                # Небо
                frame[row][col] = (' ', (20, 20, 60))
            elif row < bottom and ctype is not None:
                # Стена (или факел-клетка)
                frame[row][col] = (wallChar, wallColor)
            else:
                # Пол: классический floor casting
                dy = row - horizonRow
                if dy <= 0:
                    # Выше горизонта => небо
                    frame[row][col] = (' ', (20,20,60))
                else:
                    # camHeight = 0.5
                    p = (row - horizonRow)/(scr_h/2)
                    if abs(p)<1e-9:
                        distFloor=99999
                    else:
                        distFloor = 0.5 / p  # camHeight=0.5

                    # Интерполяция
                    u = col/(scr_w - 1)
                    rayDirX = cosA0 + (cosA1 - cosA0)*u
                    rayDirY = sinA0 + (sinA1 - sinA0)*u
                    invLen = 1.0/math.hypot(rayDirX, rayDirY)
                    rayDirX *= invLen
                    rayDirY *= invLen

                    fx = px + rayDirX*distFloor
                    fy = py + rayDirY*distFloor
                    ix, iy = int(fx), int(fy)

                    floorFog = 1.0
                    if distFloor>fogDistance:
                        floorFog = max(0.0, 1.0-(distFloor - fogDistance)/fogDistance)

                    lrF, lgF, lbF = 0,0,0
                    if 0<=ix<w and 0<=iy<h:
                        lrF, lgF, lbF = lightmap[iy][ix]

                    baseFloor=(30,50,30)
                    rF = min(255, int(baseFloor[0] + lrF*0.5*floorFog))
                    gF = min(255, int(baseFloor[1] + lgF*0.5*floorFog))
                    bF = min(255, int(baseFloor[2] + lbF*0.5*floorFog))

                    ratioFloor = distFloor/fogDistance
                    idx = int(ratioFloor*(len(floorSymbols)-1))
                    idx = max(0, min(idx, len(floorSymbols)-1))
                    floorChar = floorSymbols[idx]

                    frame[row][col] = (floorChar, (rF, gF, bF))

    return frame


def final_render_with_sprites(px, py, angle, maze, w, h, scr_w, scr_h, fov,
                              lightmap, camOffset, fogDistance,
                              torches):
    """
    Сначала рендерим стены+пол (render_frame),
    затем поверх вставляем ASCII-спрайты факелов (render_sprites).
    Возвращаем итоговый frame.
    """
    frame = render_frame(px, py, angle, maze, w, h,
                         scr_w, scr_h, fov, lightmap,
                         camOffset=camOffset,
                         fogDistance=fogDistance)
    # Затем вставляем спрайты
    render_sprites(frame, px, py, angle, torches, scr_w, scr_h, fov)
    return frame
