from cell import Cell
from grid import Grid

import cv2
import numpy as np

SCALE = 5

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
        
grid = Grid(200, 200)
cv2.namedWindow("Grid")
cv2.setMouseCallback("Grid", mouse_callback, param=grid)

if __name__ == "__main__":
    grid.populate_random(300, Cell.ALIVE)
    grid.populate_random(50, Cell.DEAD)
    print(grid[5, 5])
    print(grid.count(5, 5))
    print(grid)
    
    cell_grid = np.empty((grid.max_y, grid.max_x), dtype=np.uint8)
    
    cell_grid = grid.grid2d()
    
    # Посчитать сколько пикселей со значением 1, сколько со значением 2
    dead_count = np.sum(cell_grid == 1)
    alive_count = np.sum(cell_grid == 2)
    print(f"Dead cells: {dead_count}, Alive cells: {alive_count}")


    
    while True:
        # Преобразуем в 3-канальный цветной формат
        cell_grid = grid.grid2d().astype(np.uint8)
        cell_grid[cell_grid == 1] = 50
        cell_grid[cell_grid == 2] = 255
        # Преобразуем в 3-канальный цветной формат
        cell_grid = cv2.cvtColor(cell_grid, cv2.COLOR_GRAY2BGR)
        cell_grid = cv2.resize(cell_grid, (cell_grid.shape[1] * SCALE, cell_grid.shape[0] * SCALE), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("Grid", cell_grid)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC для выхода / ESC to exit
            break
        elif key in (ord('c'), ord('C'), 241, 209):  # 'C'/'С' для очистки (англ/рус)
            grid.clear()
            
    
    cv2.destroyAllWindows()
    
    grid.clear()
    print(grid)