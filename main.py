from cell import Cell
from grid import Grid

import cv2
import numpy as np
from random import randint

SCALE = 2
SIZE_X = 200
SIZE_Y = 200
ALIVE_START = (SIZE_X*SIZE_Y - randint(0, SIZE_X//10))
# DEAD_START = (SIZE_X*SIZE_Y - randint(0, SIZE_X//10))

def mouse_callback(event, x, y, flags, param):
    grid = param  # Получаем grid из параметра
    gx, gy = x // SCALE, y // SCALE

    if flags & cv2.EVENT_FLAG_LBUTTON:
        grid.populate([(gx, gy)], Cell.ALIVE)
    elif flags & cv2.EVENT_FLAG_RBUTTON:
        grid.populate([(gx, gy)], Cell.DEAD)
    elif flags & cv2.EVENT_FLAG_MBUTTON:
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
    delay = 2
    
    while True:
        # Преобразуем в 3-канальный цветной формат
        cell_grid = grid.grid2d().astype(np.uint8)
        cell_grid[cell_grid == 1] = 50
        cell_grid[cell_grid == 2] = 255
        # Преобразуем в 3-канальный цветной формат
        cell_grid = cv2.cvtColor(cell_grid, cv2.COLOR_GRAY2BGR)
        cell_grid = cv2.resize(cell_grid, (cell_grid.shape[1] * SCALE, cell_grid.shape[0] * SCALE), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Grid", cell_grid)
        key = cv2.waitKey(delay=delay) & 0xFF
        cv2.setWindowTitle("Grid", f"Grid - {grid.max_x}x{grid.max_y} - {delay}ms - {'PLAY' if playback else 'PAUSE'} {key=}")
        if key == 27:  # ESC для выхода / ESC to exit
            break
        elif key in (ord('c'), ord('C'), 241, 209):  # 'C'/'С' для очистки (англ/рус)
            grid.clear()
        # При нажатии пробела 'Enter' запустить/остановить симуляцию
        elif key == 13: 
            playback = not playback
        elif key == 32:
            grid.step()
        # При нажатии TAB заполнить всё поле мёртвыми клетками
        elif key == 9:  # TAB для заполнения мёртвыми клетками
            grid.fill(Cell.DEAD)
        # При нажатии CAPSLOCK заполнить всё поле живыми клетками
        elif key == 96:  # CAPSLOCK для заполнения живыми клетками
            grid.fill(Cell.ALIVE)
        # Если минус на кейпаде, то уменьшить скорость (нелинейно, но не больше 1000 мс)
        elif key == 45:  # '-' на кейпаде для уменьшения скорости
            if delay < 100:
                delay = min(1000, int(delay * 1.5))
            else:
                delay = min(1000, int(delay * 2))
        # Если плюс на кейпаде, то увеличить скорость (нелинейно, но не меньше 1 мс)
        elif key == 43:  # '+' на кейпаде для увеличения скорости
            if delay > 100:
                delay = max(1, int(delay / 2))
            else:
                delay = max(1, int(delay / 1.5))
        elif playback:
            grid.step()
        

    cv2.destroyAllWindows()
    
    grid.clear()
    print(grid)