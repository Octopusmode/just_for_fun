from cell import Cell
from grid import Grid
from patterns import Patterns

import cv2
import numpy as np
import random

import os
import time
print(os.getpid())

PATTERN_KEYS = [
    49,   # '1'
    50,   # '2'
    51,   # '3'
    52,   # '4'
    53,   # '5'
    54,   # '6'
    55,   # '7'
    56,   # '8'
    57,   # '9'
    48,   # '0'
    189,  # '-'
    187   # '='
]
PATTERN_NAMES = list(Patterns.PATTERNS.keys())



SCALE = 8
SIZE_X = 100
SIZE_Y = 100
ALIVE_START = (SIZE_X*SIZE_Y - random.randint(0, SIZE_X//10))
# DEAD_START = (SIZE_X*SIZE_Y - random.randint(0, SIZE_X//10))

def rotate_pattern(pattern, size):
    if isinstance(size, int):
        rows = cols = size
    else:
        rows, cols = size
    arr = np.array(pattern).reshape(rows, cols)
    k = random.randint(0, 3)
    return np.rot90(arr, k)

def mouse_callback(event, x, y, flags, param):
    grid = param
    gx, gy = x // SCALE, y // SCALE
    pattern_name = PATTERN_NAMES[selected_pattern_id]
    pattern = Patterns.PATTERNS[pattern_name]
    size = Patterns.PATTERN_SIZES[pattern_name]
    arr = rotate_pattern(pattern, size)
    rows, cols = arr.shape  # Получаем размеры после поворота

    if pattern_name == "dot":
        if flags & cv2.EVENT_FLAG_LBUTTON:
            grid.populate([(gx, gy)], Cell.ALIVE)
    else:
        if event == cv2.EVENT_LBUTTONDOWN:
            coords = []
            for dy in range(rows):
                for dx in range(cols):
                    if arr[dy, dx]:
                        coords.append((gx + dx, gy + dy))
            grid.populate(coords, Cell.ALIVE)
    # Обработка правой кнопки мыши
    if flags & cv2.EVENT_FLAG_RBUTTON:
        grid.populate([(gx, gy)], Cell.DEAD)
    # Обработка средней кнопки мыши
    if flags & cv2.EVENT_FLAG_MBUTTON:
        # Удаляем клетку
        grid.populate([(gx, gy)], Cell.NONE)
        
grid = Grid(SIZE_X, SIZE_Y)
cv2.namedWindow("Grid")
cv2.setMouseCallback("Grid", mouse_callback, param=grid)

if __name__ == "__main__":
    # grid.populate_random(DEAD_START, Cell.DEAD)
    grid.fill(Cell.DEAD)
    grid.populate_random(ALIVE_START, Cell.ALIVE)
    

    cell_grid = np.empty((grid.max_y, grid.max_x), dtype=np.uint8)
    
    cell_grid = grid.grid2d()
    
    # Посчитать сколько пикселей со значением 1, сколько со значением 2
    dead_count = np.sum(cell_grid == 1)
    alive_count = np.sum(cell_grid == 2)
    print(f"Dead cells: {dead_count}, Alive cells: {alive_count}")

    playback = False
    delay = 1
    
    time_prev = 0
    time_now = 0
    
    selected_pattern_id = 0
    
    step_time_ms = 0  # Время выполнения grid.step() в миллисекундах

    while True:
        arr = grid.grid2d()
        img = arr.astype(np.uint8)
        img[img == 1] = 50
        img[img == 2] = 255
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img = cv2.resize(img, (img.shape[1] * SCALE, img.shape[0] * SCALE), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Grid", img)
        
        key = cv2.waitKey(delay=delay) & 0xFF
        
        if key in PATTERN_KEYS:
            selected_pattern_id = PATTERN_KEYS.index(key) % len(PATTERN_NAMES)
        cv2.setWindowTitle(
            "Grid",
            f"Grid - {grid.max_x}x{grid.max_y} - {delay}ms - {'PLAY' if playback else 'PAUSE'} {key=} Step: {step_time_ms:.2f} ms | Pattern: {PATTERN_NAMES[selected_pattern_id]}"
        )
        if key == 27:  # ESC для выхода / ESC to exit
            break
        elif key in (ord('c'), ord('C'), 241, 209):  # 'C'/'С' для очистки (англ/рус)
            grid.clear()
        # При нажатии пробела 'Enter' запустить/остановить симуляцию
        elif key == 13:
            playback = not playback
        elif key == 32:
            t0 = time.perf_counter()
            grid.step()
            t1 = time.perf_counter()
            step_time_ms = (t1 - t0) * 1000
        # При нажатии TAB заполнить всё поле мёртвыми клетками
        elif key == 9:  # TAB для заполнения мёртвыми клетками
            grid.fill(Cell.DEAD)
            # При нажатии CAPSLOCK заполнить всё поле живыми клетками
        elif key == 96:  # CAPSLOCK для заполнения живыми клетками
            grid.fill(Cell.ALIVE)
        # Если минус на кейпаде, то уменьшить скорость (нелинейно, но не больше 1000 мс)
        elif key in (45, ord('-'), 0x4E):  # '-' на кейпаде или основной клавиатуре для уменьшения скорости
            delay = max(1, delay - 100)
        elif key in (43, ord('+'), 0x4A):  # '+'
            delay = min(1000, delay + 100)
        elif playback:
            t0 = time.perf_counter()
            grid.step()
            t1 = time.perf_counter()
            step_time_ms = (t1 - t0) * 1000
        

    cv2.destroyAllWindows()
    
    grid.clear()
    print(grid)