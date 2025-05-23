import numpy as np
from typing import List, Tuple, Union
from cell import Cell
from scipy.ndimage import convolve

class Grid():
    """
    Класс для представления двумерной сетки клеток
    """
    # Константы для максимальных размеров сетки
    MAX_X = 256
    MAX_Y = 256
    
    KERNEL = np.array([
    [1, 1, 1],
    [1, 0, 1],
    [1, 1, 1]
    ], dtype=int)

    def __init__(self, width: int = MAX_X, height: int = MAX_Y):
        Grid.MAX_X = width
        Grid.MAX_Y = height
        self.max_x = width
        self.max_y = height
        self.cells = np.empty((self.max_y, self.max_x), dtype=object)
    
    def __len__(self):
        """
        Возвращает количество клеток в сетке
        """
        return self.max_x * self.max_y
    
    def __iter__(self):
        """
        Позволяет итерироваться по клеткам в сетке
        """
        def __iter__(self):
            for y in range(self.max_y):
                for x in range(self.max_x):
                    yield self.cells[y, x]

    def __getitem__(self, item: tuple[int, int]):
        """
        Позволяет обращаться к клеткам по индексам
        """
        if isinstance(item, tuple):
            x, y = item
            return self.cells[y, x]
        else:
            raise TypeError("Index must be a tuple (x, y)")

    def __setitem__(self, key: tuple[int, int], value: Cell):
        """
        Позволяет устанавливать клетки по индексам
        """
        if isinstance(key, tuple):
            x, y = key
            if isinstance(value, Cell):
                self.cells[y, x] = value
            else:
                raise TypeError("Value must be an instance of Cell")
        else:
            raise TypeError("Index must be a tuple (x, y)")
               
    def __repr__(self):
        """
        Возвращает размер сетки и количество клеток ALIVE и DEAD
        """
        alive_count = sum(1 for cell in self.cells.flatten() if cell and cell.state == Cell.ALIVE)
        dead_count = sum(1 for cell in self.cells.flatten() if cell and cell.state == Cell.DEAD)
        return f"Grid({self.max_x=}, {self.max_y=}, {alive_count=}, {dead_count=})"

    def grid2d(self):
        if hasattr(self, '_grid2d_cache') and self._grid2d_cache is not None:
            return self._grid2d_cache
        arr = np.array([[cell.state if cell else 0 for cell in row] for row in self.cells])
        self._grid2d_cache = arr
        return arr

    def _invalidate_cache(self):
        self._grid2d_cache = None
    
    def populate_random(self, n: int, state: int = Cell.ALIVE):
        """
        Заполняет сетку случайными клетками, по умолчанию все живые (ALIVE)
        """
        self._invalidate_cache()
        _state = state
        if state not in [Cell.ALIVE, Cell.DEAD]:
            raise ValueError("State must be either Cell.ALIVE or Cell.DEAD")
        for _ in range(n):
            x = np.random.randint(0, self.max_x)
            y = np.random.randint(0, self.max_y)
            cell = Cell(x, y, _state)
            self.cells[y, x] = cell
    
    def populate(self, cells: List[Tuple[int, int]], state: int = Cell.ALIVE):
        """
        Заполняет сетку клетками по заданным координатам
        """
        self._invalidate_cache()
        _state = state
        # FIXME Поправить чтобы можно было передавать состояние NONE
        if state not in [Cell.ALIVE, Cell.DEAD, Cell.NONE]:
            raise ValueError("State must be either Cell.ALIVE or Cell.DEAD or Cell.NONE")
        if not isinstance(cells, list):
            raise TypeError("Cells must be a list of tuples (x, y)")
        for x, y in cells:
            if 0 <= x < self.max_x and 0 <= y < self.max_y:
                cell = Cell(x, y, _state)
                self.cells[y, x] = cell
            else:
                raise IndexError("Coordinates out of bounds")
            
            
    def count(self, x: int, y: int, state: int = Cell.ALIVE) -> int:
        """
        Считает количество клеток с заданным состоянием вокруг данной клетки

        :param x: координата x клетки
        :param y: координата y клетки
        :param state: состояние клетки, которое нужно считать (по умолчанию ALIVE)
        :return: количество клеток с заданным состоянием вокруг (x, y)
        """
        neighbors = [
            (x + dx, y + dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]
        count = 0
        for nx, ny in neighbors:
            if 0 <= nx < self.max_x and 0 <= ny < self.max_y:
                cell = self.cells[ny, nx]
                if isinstance(cell, Cell) and cell.state == state:
                    count += 1
        return count
    
    # def step(self):
    #     self._invalidate_cache()
    #     new_cells = np.empty_like(self.cells)
    #     arr = self.grid2d()
    #     for y in range(self.max_y):
    #         for x in range(self.max_x):
    #             cell = self.cells[y, x]
    #             state = cell.state if cell else Cell.NONE
    #             alive_neighbors = self.count(x, y, Cell.ALIVE)
    #             # Пример для "Жизни"
    #             if state == Cell.ALIVE:
    #                 if alive_neighbors < 2 or alive_neighbors > 3:
    #                     new_state = Cell.DEAD
    #                 else:
    #                     new_state = Cell.ALIVE
    #             else:
    #                 if alive_neighbors == 3:
    #                     new_state = Cell.ALIVE
    #                 else:
    #                     new_state = Cell.DEAD
    #             # Только если состояние изменилось — создаём новый объект
    #             if state != new_state:
    #                 new_cells[y, x] = Cell(x, y, new_state)
    #             else:
    #                 new_cells[y, x] = cell
    #     self.cells = new_cells
    
    # def step(self):
    #     self._invalidate_cache()
    #     arr = self.grid2d()
    #     alive_mask = (arr == Cell.ALIVE).astype(int)
    #     neighbors = convolve(alive_mask, self.KERNEL, mode='constant', cval=0)
    #     new_cells = np.empty_like(self.cells)
    #     for y in range(self.max_y):
    #         for x in range(self.max_x):
    #             state = arr[y, x]
    #             n = neighbors[y, x]
    #             if state == Cell.ALIVE:
    #                 new_state = Cell.ALIVE if 2 <= n <= 3 else Cell.DEAD
    #             else:
    #                 new_state = Cell.ALIVE if n == 3 else Cell.DEAD
    #             if state != new_state:
    #                 new_cells[y, x] = Cell(x, y, new_state)
    #             else:
    #                 new_cells[y, x] = self.cells[y, x]
    #     self.cells = new_cells
    
    def step(self):
        self._invalidate_cache()
        arr = self.grid2d()
        alive_mask = (arr == Cell.ALIVE).astype(int)
        # Меняем mode='constant' на mode='wrap'
        neighbors = convolve(alive_mask, self.KERNEL, mode='wrap')
        new_cells = np.empty_like(self.cells)
        for y in range(self.max_y):
            for x in range(self.max_x):
                state = arr[y, x]
                n = neighbors[y, x]
                if state == Cell.ALIVE:
                    new_state = Cell.ALIVE if 2 <= n <= 3 else Cell.DEAD
                else:
                    new_state = Cell.ALIVE if n == 3 else Cell.DEAD
                if state != new_state:
                    new_cells[y, x] = Cell(x, y, new_state)
                else:
                    new_cells[y, x] = self.cells[y, x]
        self.cells = new_cells

    def fill(self, state: int = Cell.DEAD):
        """
        Заполняет сетку клетками заданного состояния
        """
        self._invalidate_cache()
        for y in range(self.max_y):
            for x in range(self.max_x):
                cell = Cell(x, y, state)
                self.cells[y, x] = cell

    def clear(self):
        """
        Очищает сетку, удаляя все живие и мёртвые клетки
        """
        self._invalidate_cache()
        self.cells.fill(None)