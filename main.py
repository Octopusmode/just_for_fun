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

SCALE = 4
SIZE_X = 500
SIZE_Y = 300
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
    state = param  # param теперь словарь с grid, playback, mouse_down
    grid = state["grid"]
    gx, gy = x // SCALE, y // SCALE
    pattern_name = PATTERN_NAMES[state["selected_pattern_id"]]
    pattern = Patterns.PATTERNS[pattern_name]
    size = Patterns.PATTERN_SIZES[pattern_name]
    arr = rotate_pattern(pattern, size)
    rows, cols = arr.shape

    # Управление mouse_down и playback через state
    if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN, cv2.EVENT_MBUTTONDOWN):
        state["mouse_down"] = True
        state["playback"] = False
    elif event in (cv2.EVENT_LBUTTONUP, cv2.EVENT_RBUTTONUP, cv2.EVENT_MBUTTONUP):
        state["mouse_down"] = False

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
    if flags & cv2.EVENT_FLAG_RBUTTON:
        grid.populate([(gx, gy)], Cell.DEAD)
    if flags & cv2.EVENT_FLAG_MBUTTON:
        grid.populate([(gx, gy)], Cell.NONE)
        
grid = Grid(SIZE_X, SIZE_Y)
cv2.namedWindow("Grid")

if __name__ == "__main__":
    # grid.populate_random(DEAD_START, Cell.DEAD)
    grid.fill(Cell.DEAD)
    grid.populate_random(ALIVE_START, Cell.ALIVE)
    
    state = {
        "grid": grid,
        "playback": False,
        "mouse_down": False,
        "selected_pattern_id": 0,
    }

    cv2.setMouseCallback("Grid", mouse_callback, param=state)

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

    arr_prev = grid.grid2d()
    fade_arr = np.zeros_like(arr_prev, dtype=np.uint8)

    while True:
        arr = grid.grid2d()
        # fade_arr = np.where(arr_prev == Cell.ALIVE, 255, np.maximum(fade_arr - 5, 0)).astype(np.uint8)
        img = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
        img[..., 2] = fade_arr

        mask_prev_alive = (arr_prev == Cell.ALIVE)
        img[mask_prev_alive] = [0, 0, 50]  # Красный для предыдущих живых клеток

        mask_alive = (arr == Cell.ALIVE)
        img[mask_alive] = [255, 255, 255]

        img = cv2.resize(img, (img.shape[1] * SCALE, img.shape[0] * SCALE), interpolation=cv2.INTER_NEAREST)
        if SCALE > 3:
            for y in range(0, img.shape[0], SCALE):
                img[y:y+1, :] = 0
            for x in range(0, img.shape[1], SCALE):
                img[:, x:x+1] = 0

        cv2.imshow("Grid", img)

        key = cv2.waitKey(delay=delay) & 0xFF

        if key in PATTERN_KEYS:
            state["selected_pattern_id"] = PATTERN_KEYS.index(key) % len(PATTERN_NAMES)
        cv2.setWindowTitle(
            "Grid",
            f"Grid - {grid.max_x}x{grid.max_y} - {delay}ms - {'PLAY' if state['playback'] else 'PAUSE'} {key=} Step: {step_time_ms:.2f} ms | Pattern: {PATTERN_NAMES[state['selected_pattern_id']]}"
        )
        if key == 27:
            break
        elif key in (ord('c'), ord('C'), 241, 209):
            grid.clear()
        elif key == 13:
            state["playback"] = not state["playback"]
        elif key == 32:
            t0 = time.perf_counter()
            grid.step()
            t1 = time.perf_counter()
            step_time_ms = (t1 - t0) * 1000
            fade_arr = np.where(arr_prev == Cell.ALIVE, 255, np.maximum(fade_arr - 5, 0)).astype(np.uint8)
            arr_prev = arr.copy()
        elif key == 9:
            grid.fill(Cell.DEAD)
        elif key == 96:
            grid.fill(Cell.ALIVE)
        elif key in (45, ord('-'), 0x4E):
            delay = max(1, delay - 100)
        elif key in (43, ord('+'), 0x4A):
            delay = min(1000, delay + 100)
        elif state["playback"] and not state["mouse_down"]:
            t0 = time.perf_counter()
            grid.step()
            t1 = time.perf_counter()
            step_time_ms = (t1 - t0) * 1000
            fade_arr = np.where(arr_prev == Cell.ALIVE, 255, np.maximum(fade_arr - 5, 0)).astype(np.uint8)
            arr_prev = arr.copy()

    cv2.destroyAllWindows()
    
    grid.clear()
    print(grid)