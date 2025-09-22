import pygame
import threading
import random
import time

# Game settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
CELL_SIZE = 20
FPS = 15

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Multithreaded Snake Game')
        self.clock = pygame.time.Clock()
        self.reset()
        self.running = True
        self.lock = threading.Lock()

    def reset(self):
        self.snake = [(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.spawn_food()
        self.score = 0

    def spawn_food(self):
        while True:
            x = random.randint(0, (WINDOW_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def handle_input(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    with self.lock:
                        if event.key == pygame.K_UP and self.direction != DOWN:
                            self.next_direction = UP
                        elif event.key == pygame.K_DOWN and self.direction != UP:
                            self.next_direction = DOWN
                        elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                            self.next_direction = LEFT
                        elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                            self.next_direction = RIGHT
            time.sleep(0.01)

    def update(self):
        while self.running:
            with self.lock:
                self.direction = self.next_direction
            head_x, head_y = self.snake[0]
            dx, dy = self.direction
            new_head = (head_x + dx * CELL_SIZE, head_y + dy * CELL_SIZE)

            # Check collision with walls
            if (new_head[0] < 0 or new_head[0] >= WINDOW_WIDTH or
                new_head[1] < 0 or new_head[1] >= WINDOW_HEIGHT):
                self.running = False
                break

            # Check collision with self
            if new_head in self.snake:
                self.running = False
                break

            self.snake.insert(0, new_head)

            # Check food collision
            if new_head == self.food:
                self.score += 1
                self.spawn_food()
            else:
                self.snake.pop()

            time.sleep(1.0 / FPS)

    def draw(self):
        self.screen.fill(BLACK)
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(self.screen, RED, (*self.food, CELL_SIZE, CELL_SIZE))
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        pygame.display.flip()

    def run(self):
        input_thread = threading.Thread(target=self.handle_input)
        update_thread = threading.Thread(target=self.update)
        input_thread.start()
        update_thread.start()

        while self.running:
            self.draw()
            self.clock.tick(FPS)

        input_thread.join()
        update_thread.join()
        pygame.quit()
        print(f'Game Over! Your score: {self.score}')

if __name__ == "__main__":
    SnakeGame().run()
