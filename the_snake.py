import sys
import pygame
from random import choice, randint

# Константы для размеров поля и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)  # Чёрный
BORDER_COLOR = (93, 216, 228)  # Цвет границы ячейки
APPLE_COLOR = (255, 0, 0)       # Красный (яблоко)
SNAKE_COLOR = (0, 255, 0)      # Зелёный (змейка)

# Скорость движения змейки
SPEED = 20

# Инициализация Pygame и настройка игрового окна
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()



class GameObject:
    """Базовый класс, от которого наследуются все игровые объекты. Содержит общие атрибуты: позиция и цвет."""

    def __init__(self, position=None, body_color=None):
        """Конструктор базового игрового объекта.

        Args:
            position (tuple): координаты позиции объекта (x, y).
            body_color (tuple): цвет объекта в формате RGB.
        """
        if position is None:
            self.position = (320, 240)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """Абстрактный метод для отрисовки объекта на экране.

        Args:
            surface (pygame.Surface): поверхность, на которой рисуем.
        """
        pass



class Apple(GameObject):
    """Класс, описывающий яблоко. Наследуется от GameObject. Появляется в случайном месте игрового поля."""

    def __init__(self):
        """Инициализирует яблоко с красным цветом и случайной позицией."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайные координаты для яблока, выровненные по сетке."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Отрисовывает яблоко на игровом поле.

        Args:
            surface (pygame.Surface): поверхность для отрисовки.
        """
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)



class Snake(GameObject):
    """Дочерний класс, описывающий змейку."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Конструктор, создающий змейку.

        Args:
            body_color (tuple): цвет змейки в формате RGB.
        """
        super().__init__(position=(320, 240), body_color=body_color)
        self.reset()
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки, если было задано новое."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Возвращает позицию головы змейки.

        Returns:
            tuple: координаты головы змейки (x, y).
        """
        return self.positions[0]

    def move(self):
        """Обновляет позицию змейки на основе текущего направления."""
        head_x, head_y = self.get_head_position()
        new_x = (head_x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        self.positions.insert(0, (new_x, new_y))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface):
        """Отрисовывает змейку на игровом поле.

        Args:
            surface (pygame.Surface): поверхность для отрисовки.
        """
        # Отрисовываем все сегменты змейки
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Затираем последний сегмент, если он был удалён
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку к начальному состоянию при перезапуске игры."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None
        self.last = None



def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        game_object (Snake): объект змейки для управления.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()



def main():
    """Основной игровой цикл."""
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка столкновения головы змейки с яблоком
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

            # Убедимся, что яблоко не появляется на змейке
            while apple.position in snake.positions:
                apple.randomize_position()