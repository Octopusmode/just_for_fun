"""
Вводные:
Мёртвые кретки - DEAD
Живые клетки - ALIVE
Состояние клетки - 0 (DEAD) или 1 (ALIVE)
Cell - Класс для представления клетки в сетке
Grid - Класс для представления двумерной сетки клеток

Мертвые клетки - DEAD не удаляются из сетки, а просто становятся мертвыми
"""

from typing import List, Tuple, Union
from random import randint, choice

class Cell():
    """
    Класс для представления клетки в сетке
    """
    # Константы для состояний клетки
    NONE = 0
    DEAD = 1
    ALIVE = 2
    
    def __init__(self, x: int, y: int, state: int = 1):
        assert 0 <= state < 16
        self._x: int = x
        self._y: int = y
        self._state: int = state

    @property
    def state(self):
            return self._state
        
    @state.setter
    def state(self, new_state: int):
        assert 0 <= new_state < 16
        self._state = new_state
        
    def __repr__(self):
        x = self._x
        y = self._y
        state = self._state
        return f'Cell({x=}, {y=}, {state=})'
    

    
