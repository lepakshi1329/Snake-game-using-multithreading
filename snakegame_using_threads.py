import pygame
import threading
import random
import time

# Game settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
CELL_SIZE = 20
FPS = 8  # Slower for more playable speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
LIME = (50, 205, 50)
GOLD = (255, 215, 0)

# Snake color palette
SNAKE_COLORS = [GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN, PINK, LIME, GOLD]

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Multithreaded Snake Game - Use Arrow Keys to Play!')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset()
        self.running = True
        self.game_over = False
        self.paused = False
        self.lock = threading.Lock()
    
    def reset(self):
        """Reset game state for new game"""
        center_x = (WINDOW_WIDTH // 2 // CELL_SIZE) * CELL_SIZE
        center_y = (WINDOW_HEIGHT // 2 // CELL_SIZE) * CELL_SIZE
        
        self.snake = [
            (center_x, center_y),
            (center_x - CELL_SIZE, center_y),
            (center_x - 2*CELL_SIZE, center_y)
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.color_index = 0  # Track current color
    
    def spawn_food(self):
        """Spawn food at random location not occupied by snake"""
        while True:
            x = random.randint(0, (WINDOW_WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            y = random.randint(0, (WINDOW_HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def update_game_logic(self):
        """Game logic update thread"""
        while self.running:
            if not self.paused and not self.game_over:
                try:
                    with self.lock:
                        # Update direction
                        self.direction = self.next_direction
                    
                    # Calculate new head position
                    head_x, head_y = self.snake[0]
                    dx, dy = self.direction
                    new_head = (head_x + dx * CELL_SIZE, head_y + dy * CELL_SIZE)
                    
                    # Check wall collision
                    if (new_head[0] < 0 or new_head[0] >= WINDOW_WIDTH or
                        new_head[1] < 0 or new_head[1] >= WINDOW_HEIGHT):
                        with self.lock:
                            self.game_over = True
                        continue
                    
                    # Check self collision
                    if new_head in self.snake:
                        with self.lock:
                            self.game_over = True
                        continue
                    
                    # Move snake
                    with self.lock:
                        self.snake.insert(0, new_head)
                        
                        # Check food collision
                        if new_head == self.food:
                            self.score += 10
                            # Change color when eating food
                            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)
                            self.spawn_food()
                        else:
                            self.snake.pop()
                
                except Exception as e:
                    print(f"Game logic error: {e}")
                    with self.lock:
                        self.running = False
            
            # Control game speed
            time.sleep(1.0 / FPS)
    
    def draw(self):
        """Render the game"""
        self.screen.fill(BLACK)
        
        with self.lock:
            if not self.game_over:
                # Get current snake color
                snake_color = SNAKE_COLORS[self.color_index]
                
                # Draw snake with current color
                for i, segment in enumerate(self.snake):
                    if i == 0:  # Head - slightly brighter
                        head_color = tuple(min(255, c + 50) for c in snake_color)
                        pygame.draw.rect(self.screen, head_color, (*segment, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(self.screen, WHITE, (*segment, CELL_SIZE, CELL_SIZE), 2)
                    else:  # Body segments
                        pygame.draw.rect(self.screen, snake_color, (*segment, CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(self.screen, WHITE, (*segment, CELL_SIZE, CELL_SIZE), 1)
                
                # Draw food
                pygame.draw.rect(self.screen, RED, (*self.food, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, WHITE, (*self.food, CELL_SIZE, CELL_SIZE), 2)
            
            # Draw score
            score_text = self.font.render(f'Score: {self.score}', True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Draw instructions
            if not self.game_over:
                if self.paused:
                    pause_text = self.font.render('PAUSED - Press SPACE to resume', True, WHITE)
                    text_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                    pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
                    pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10), 2)
                    self.screen.blit(pause_text, text_rect)
                else:
                    # Show controls and color info at bottom
                    controls = f"Arrow Keys: move • SPACE: pause • ESC: quit • Color changes: {self.score//10}"
                    control_text = self.small_font.render(controls, True, WHITE)
                    self.screen.blit(control_text, (10, WINDOW_HEIGHT - 25))
            else:
                # Game over screen
                game_over_text = self.font.render('GAME OVER!', True, RED)
                score_text = self.font.render(f'Final Score: {self.score}', True, WHITE)
                restart_text = self.small_font.render('Press R to restart • ESC to quit', True, WHITE)
                
                # Center the text
                go_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 40))
                score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 40))
                
                # Draw background rectangles
                pygame.draw.rect(self.screen, BLACK, go_rect.inflate(20, 10))
                pygame.draw.rect(self.screen, RED, go_rect.inflate(20, 10), 3)
                
                self.screen.blit(game_over_text, go_rect)
                self.screen.blit(score_text, score_rect)
                self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("Snake Game Started!")
        print("Controls:")
        print("- Arrow Keys: Move snake")
        print("- SPACE: Pause/Resume")
        print("- R: Restart (when game over)")
        print("- ESC: Quit")
        
        # Start the update thread
        update_thread = threading.Thread(target=self.update_game_logic, daemon=True)
        update_thread.start()
        
        # Main thread handles events and rendering
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    elif event.key == pygame.K_SPACE:
                        if not self.game_over:
                            self.paused = not self.paused
                    
                    elif event.key == pygame.K_r and self.game_over:
                        with self.lock:
                            self.reset()
                    
                    elif not self.paused and not self.game_over:
                        with self.lock:
                            if event.key == pygame.K_UP and self.direction != DOWN:
                                self.next_direction = UP
                            elif event.key == pygame.K_DOWN and self.direction != UP:
                                self.next_direction = DOWN
                            elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                                self.next_direction = LEFT
                            elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                                self.next_direction = RIGHT
            
            # Draw the game
            self.draw()
            
            # Control frame rate (smooth rendering)
            self.clock.tick(60)
        
        # Cleanup
        with self.lock:
            self.running = False
        
        update_thread.join(timeout=1.0)
        pygame.quit()
        print(f'\nThanks for playing! Final score: {self.score}')

if __name__ == "__main__":
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Keep console open to see final score
        input("\nPress Enter to close...")
