import pygame
import random
import os

# Initialize
pygame.init()
WIDTH, HEIGHT = 800, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Escape: Entangled Mazes")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Constants
TILE = 40
ROWS = HEIGHT // 2 // TILE
COLS = WIDTH // TILE

# Load Images
def load(name):
    return pygame.transform.scale(pygame.image.load(os.path.join("assets", name)), (TILE, TILE))

player_img = load("player.png")
wall_img = load("wall.png")
key_img = load("key.png")
exit_img = load("exit.png")
obstacle_img = load("obstacle.png")
check_img = load("check.png")
cross_img = load("cross.png")

# Quantum States
state = "|0>"
quantum_mode = False
twin_player = None

# Game Elements
walls_0 = []
walls_1 = []
keys = []
exit_rect = None
obstacles = []

# Build Maze
def create_maze():
    global walls_0, walls_1, keys, exit_rect, obstacles
    walls_0.clear()
    walls_1.clear()
    keys.clear()
    obstacles.clear()

    for row in range(ROWS):
        for col in range(COLS):
            rect_top = pygame.Rect(col * TILE, row * TILE, TILE, TILE)
            rect_bot = pygame.Rect(col * TILE, row * TILE + HEIGHT // 2, TILE, TILE)

            if random.random() < 0.15:
                walls_0.append(rect_top)
            if random.random() < 0.15:
                walls_1.append(rect_bot)

            if random.random() < 0.02:
                if rect_top not in walls_0:
                    keys.append(rect_top)
            if random.random() < 0.02:
                if rect_bot not in walls_1:
                    keys.append(rect_bot)

            if random.random() < 0.08:
                obstacles.append(rect_top if random.choice([True, False]) else rect_bot)

    exit_rect = pygame.Rect(WIDTH - TILE, TILE if random.choice([0, 1]) == 0 else HEIGHT // 2 + TILE, TILE, TILE)

create_maze()

# Player
player = pygame.Rect(TILE, TILE, TILE, TILE)
has_key = False

# Instructions Screen
def show_instructions():
    screen.fill((0, 0, 0))
    instructions = [
        "Quantum Escape: Entangled Mazes",
        "",
        "Instructions:",
        "- Navigate the maze using arrow keys.",
        "- X gate (press 'X') switches between |0> and |1> states.",
        "- H gate (press 'H') toggles quantum superposition: creates twin player.",
        "- Z gate (press 'Z') flips between |+> and |-> states in quantum mode.",
        "- In quantum mode, player cannot move. Obstacles auto-move upward.",
        "- Use LEFT/RIGHT keys to move obstacles horizontally in quantum mode.",
        "- Collect the key and reach the exit to win.",
        "- Avoid obstacles. In quantum mode, collisions trigger measurement.",
        "",
        "Press any key to start..."
    ]
    for i, line in enumerate(instructions):
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (40, 40 + i * 30))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

show_instructions()

# Clear screen on win/loss
def clear_screen(message):
    screen.fill((0, 0, 0))
    text = font.render(message, True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Draw Function
def draw():
    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (255, 255, 255), (0, HEIGHT//2), (WIDTH, HEIGHT//2), 2)

    for w in walls_0:
        screen.blit(wall_img, w)
    for w in walls_1:
        screen.blit(wall_img, w)
    for k in keys:
        screen.blit(key_img, k)
    for o in obstacles:
        screen.blit(obstacle_img, o)

    screen.blit(exit_img, exit_rect)
    screen.blit(player_img, player)
    if twin_player:
        screen.blit(player_img, twin_player)

    # UI
    state_text = font.render(f"State: {state}", True, (0, 255, 255))
    screen.blit(state_text, (WIDTH - 200, 10))
    screen.blit(font.render("Key:", True, (255, 255, 0)), (WIDTH - 200, 40))
    screen.blit(check_img if has_key else cross_img, (WIDTH - 130, 40))

    pygame.display.flip()

# State Functions
def apply_gate(gate):
    global state, quantum_mode, twin_player
    if gate == "X" and not quantum_mode:
        if state == "|0>":
            state = "|1>"
            player.y += HEIGHT // 2
        else:
            state = "|0>"
            player.y -= HEIGHT // 2
    elif gate == "Z" and quantum_mode:
        state = "|->" if state == "|+>" else "|+>"
    elif gate == "H":
        if state == "|0>":
            state = "|+>"
            quantum_mode = True
            twin_player = player.copy()
            twin_player.y += HEIGHT // 2
        elif state == "|1>":
            state = "|->"
            quantum_mode = True
            twin_player = player.copy()
            twin_player.y -= HEIGHT // 2
        elif state == "|+>":
            state = "|0>"
            quantum_mode = False
            twin_player = None
        elif state == "|->":
            state = "|1>"
            quantum_mode = False
            twin_player = None

def measure_collapse():
    global state, quantum_mode, player, twin_player
    result = random.choice(["|0>", "|1>"])
    if result == "|0>":
        state = "|0>"
        player.y = player.y % (HEIGHT // 2)
    else:
        state = "|1>"
        player.y = player.y % (HEIGHT // 2) + HEIGHT // 2
    quantum_mode = False
    twin_player = None

# Game Loop
running = True
while running:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys_pressed = pygame.key.get_pressed()
    dx = dy = 0

    if not quantum_mode:
        if keys_pressed[pygame.K_LEFT]: dx = -TILE
        if keys_pressed[pygame.K_RIGHT]: dx = TILE
        if keys_pressed[pygame.K_UP]: dy = -TILE
        if keys_pressed[pygame.K_DOWN]: dy = TILE

        new_pos = player.move(dx, dy)
        if state == "|0>":
            if not any(w.colliderect(new_pos) for w in walls_0):
                player = new_pos
        else:
            if not any(w.colliderect(new_pos) for w in walls_1):
                player = new_pos

    # Quantum gate keys
    if keys_pressed[pygame.K_x]: apply_gate("X")
    if keys_pressed[pygame.K_z]: apply_gate("Z")
    if keys_pressed[pygame.K_h]: apply_gate("H")

    # Random gate
    r = random.randint(0, 300)
    if r in [100, 200]: apply_gate("X")
    if r in [50, 250]: apply_gate("Z")
    if r == 150: apply_gate("H")

    # Obstacle movement
    if quantum_mode:
        dx = 0
        if keys_pressed[pygame.K_LEFT]: dx = -TILE
        if keys_pressed[pygame.K_RIGHT]: dx = TILE
        for i, obs in enumerate(obstacles):
            obstacles[i].x += dx
            obstacles[i].y -= 2
            if obstacles[i].y < 0:
                obstacles[i].y = HEIGHT - TILE
    else:
        for i, obs in enumerate(obstacles):
            obstacles[i].x -= 2
            if obstacles[i].x < -TILE:
                obstacles[i].x = WIDTH

    # Collisions
    for obs in obstacles:
        if player.colliderect(obs) or (twin_player and twin_player.colliderect(obs)):
            if quantum_mode:
                measure_collapse()
            else:
                clear_screen("You were hit! Game Over.")
                running = False

    for k in keys[:]:
        if player.colliderect(k):
            keys.remove(k)
            has_key = True

    if has_key and player.colliderect(exit_rect):
        clear_screen("You escaped the quantum maze!")
        running = False

    draw()

pygame.quit()
