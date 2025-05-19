import numpy as np
from typing import List, Tuple, Union
from cell import Cell

class Grid():
    """
    Класс для представления двумерной сетки клеток
    """
    # Константы для максимальных размеров сетки
    MAX_X = 256
    MAX_Y = 256

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
        """
        Возвращает двумерный массив состояний клеток
        """
        return np.array([[cell.state if cell else 0 for cell in row] for row in self.cells])
    
    def populate_random(self, n: int, state: int = Cell.ALIVE):
        """
        Заполняет сетку случайными клетками, по умолчанию все живые (ALIVE)
        """
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
    
    def step(self):
        """
        Выполняет один шаг симуляции, обновляя состояние клеток по следующим правилам:
        1. Если клетка живая (ALIVE) и у неё меньше 2-х или больше 3-х живых соседей, она умирает (DEAD).
        2. Если клетка живая (ALIVE) и у неё 2 или 3 живых соседа, она остаётся живой (ALIVE).
        3. Если клетка мёртвая (DEAD) и у неё ровно 3 живых соседа, она становится живой (ALIVE).
        4. В противном случае клетка остаётся мёртвой (DEAD).
        
        """
        new_cells = np.empty((self.max_y, self.max_x), dtype=object)
        for y in range(self.max_y):
            for x in range(self.max_x):
                cell = self.cells[y, x]
                if isinstance(cell, Cell):
                    alive_neighbors = self.count(x, y, Cell.ALIVE)
                    if cell.state == Cell.ALIVE:
                        if alive_neighbors < 2 or alive_neighbors > 3:
                            new_cells[y, x] = Cell(x, y, Cell.DEAD)
                        else:
                            new_cells[y, x] = Cell(x, y, Cell.ALIVE)
                    elif cell.state == Cell.DEAD:
                        if alive_neighbors == 3:
                            new_cells[y, x] = Cell(x, y, Cell.ALIVE)
                        else:
                            new_cells[y, x] = Cell(x, y, Cell.DEAD)
                else:
                    new_cells[y, x] = None
        self.cells = new_cells
        
    def fill(self, state: int = Cell.DEAD):
        """
        Заполняет сетку клетками заданного состояния
        """
        for y in range(self.max_y):
            for x in range(self.max_x):
                cell = Cell(x, y, state)
                self.cells[y, x] = cell

    def clear(self):
        """
        Очищает сетку, удаляя все живие и мёртвые клетки
        """
        self.cells.fill(None)