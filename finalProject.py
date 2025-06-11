import pygame
import random
import sys

# Constants
BLOCK_SIZE = 30
COLUMNS = 20
ROWS = 20
WIDTH = COLUMNS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE
FPS = 60
TIMER_DURATION = 120  # 2 minutes in seconds

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLOCK_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255),
    (255, 255, 0), (255, 0, 255), (0, 255, 255)
]

# Block shapes
SHAPES = [
    [(0, 0)],
    [(0, 0), (1, 0)],
    [(0, 0), (0, 1)],
    [(0, 0), (1, 0), (0, 1)],
    [(0, 0), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Block Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

grid = [[None for _ in range(COLUMNS)] for _ in range(ROWS)]
fall_delay = 500
last_fall = pygame.time.get_ticks()
paused = False
score = 0
player = "Player1"
start_time = pygame.time.get_ticks()
game_over = False

# Pre-place more blocks randomly
for _ in range(60):
    x = random.randint(0, COLUMNS - 1)
    y = random.randint(ROWS - 8, ROWS - 1)
    color = random.choice(BLOCK_COLORS)
    grid[y][x] = color

def new_shape():
    shape = random.choice(SHAPES)
    color = random.choice(BLOCK_COLORS)
    return {'blocks': shape, 'x': COLUMNS // 2, 'y': 0, 'color': color}

active = new_shape()

def draw():
    screen.fill(BLACK)

    # Draw grid
    for y in range(ROWS):
        for x in range(COLUMNS):
            color = grid[y][x]
            if color:
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # Draw active shape
    for dx, dy in active['blocks']:
        px = active['x'] + dx
        py = active['y'] + dy
        if 0 <= px < COLUMNS and 0 <= py < ROWS:
            pygame.draw.rect(screen, active['color'], (px * BLOCK_SIZE, py * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw timer
    elapsed = (pygame.time.get_ticks() - start_time) // 1000
    remaining = max(0, TIMER_DURATION - elapsed)
    timer_text = font.render(f"Time Left: {remaining}s", True, WHITE)
    screen.blit(timer_text, (WIDTH - 200, 10))

    pygame.display.flip()

def can_move(dx, dy):
    for bx, by in active['blocks']:
        x = active['x'] + bx + dx
        y = active['y'] + by + dy
        if x < 0 or x >= COLUMNS or y < 0 or y >= ROWS or grid[y][x]:
            return False
    return True

def lock_shape():
    for dx, dy in active['blocks']:
        x = active['x'] + dx
        y = active['y'] + dy
        if 0 <= x < COLUMNS and 0 <= y < ROWS:
            grid[y][x] = active['color']
    clear_rows_and_matches()

def clear_rows_and_matches():
    global score
    matched_positions = set()

    # Check horizontal matches
    for y in range(ROWS):
        count = 1
        for x in range(1, COLUMNS):
            if grid[y][x] and grid[y][x] == grid[y][x - 1]:
                count += 1
            else:
                if count >= 3:
                    for i in range(x - count, x):
                        matched_positions.add((y, i))
                count = 1
        if count >= 3:
            for i in range(COLUMNS - count, COLUMNS):
                matched_positions.add((y, i))

    # Check vertical matches
    for x in range(COLUMNS):
        count = 1
        for y in range(1, ROWS):
            if grid[y][x] and grid[y][x] == grid[y - 1][x]:
                count += 1
            else:
                if count >= 3:
                    for i in range(y - count, y):
                        matched_positions.add((i, x))
                count = 1
        if count >= 3:
            for i in range(ROWS - count, ROWS):
                matched_positions.add((i, x))

    # Clear matched blocks and update score
    for y, x in matched_positions:
        grid[y][x] = None
    score += len(matched_positions) * 10

    # Drop blocks after match clear
    if matched_positions:
        for x in range(COLUMNS):
            stack = [grid[y][x] for y in range(ROWS) if grid[y][x]]
            for y in range(ROWS):
                grid[y][x] = None
            for i, color in enumerate(reversed(stack)):
                grid[ROWS - 1 - i][x] = color

    # Clear full rows
    full_rows = [i for i, row in enumerate(grid) if all(row)]
    for i in full_rows:
        del grid[i]
        grid.insert(0, [None for _ in range(COLUMNS)])
    score += len(full_rows) * 100

def toggle_pause():
    global paused
    paused = not paused

# Game loop
running = True
while running:
    clock.tick(FPS)

    elapsed_seconds = (pygame.time.get_ticks() - start_time) // 1000
    if elapsed_seconds >= TIMER_DURATION:
        game_over = True
        running = False

    if not paused:
        now = pygame.time.get_ticks()
        # Increase difficulty
        if score > 160:
            fall_delay = 300
        if now - last_fall > fall_delay:
            if can_move(0, 1):
                active['y'] += 1
            else:
                lock_shape()
                active = new_shape()
                if not can_move(0, 0):
                    game_over = True
                    running = False
            last_fall = now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and can_move(-1, 0):
                active['x'] -= 1
            elif event.key == pygame.K_RIGHT and can_move(1, 0):
                active['x'] += 1
            elif event.key == pygame.K_DOWN and can_move(0, 1):
                active['y'] += 1
            elif event.key == pygame.K_SPACE:
                toggle_pause()

    draw()

# Game Over screen
screen.fill(BLACK)
end_text = font.render(f"Game Over, {player}! Final Score: {score}", True, WHITE)
screen.blit(end_text, (WIDTH // 2 - end_text.get_width() // 2, HEIGHT // 2 - end_text.get_height() // 2))
pygame.display.flip()
pygame.time.delay(4000)
pygame.quit()
sys.exit()
