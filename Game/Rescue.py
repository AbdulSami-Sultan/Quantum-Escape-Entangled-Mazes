import pygame
import random

# Pygame setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quantum Rescue: Schr\u00f6dinger's Crew")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game state
player_state = "|0>"
quantum_mode = False
score = 0
font = pygame.font.SysFont('Arial', 24)

# Player ship
ship = pygame.Rect(100, SCREEN_HEIGHT // 2 - 20, 40, 20)

# Crew
crew = []
crew_spawn_delay = 120  # frames
crew_timer = 0

# Functions
def draw_ship():
    pygame.draw.rect(screen, GREEN if not quantum_mode else BLUE, ship)

def spawn_crew():
    y = random.randint(0, SCREEN_HEIGHT - 20)
    state = random.choice(["|0>", "|1>", "|+>", "|->"])
    rect = pygame.Rect(SCREEN_WIDTH, y, 30, 20)
    return {"rect": rect, "state": state, "saved": False}

def draw_crew():
    for c in crew:
        pygame.draw.rect(screen, RED, c["rect"])
        label = font.render(c["state"], True, WHITE)
        screen.blit(label, (c["rect"].x, c["rect"].y - 20))

def move_crew():
    for c in crew:
        c["rect"].x -= 2

def check_rescue():
    global score
    for c in crew:
        if not c["saved"] and ship.colliderect(c["rect"]):
            if c["state"] == player_state:
                c["saved"] = True
                score += 1
            else:
                score -= 1
            c["rect"].x = -100

# Main loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]: ship.y -= 5
    if keys[pygame.K_DOWN]: ship.y += 5
    if keys[pygame.K_x]:
        if player_state == "|0>":
            player_state = "|1>"
        elif player_state == "|1>":
            player_state = "|0>"
    if keys[pygame.K_z]:
        if player_state == "|+>":
            player_state = "|->"
        elif player_state == "|->":
            player_state = "|+>"
    if keys[pygame.K_h]:
        if player_state == "|0>":
            player_state = "|+>"
            quantum_mode = True
        elif player_state == "|1>":
            player_state = "|->"
            quantum_mode = True
        elif player_state == "|+>":
            player_state = "|0>"
            quantum_mode = False
        elif player_state == "|->":
            player_state = "|1>"
            quantum_mode = False

    # Crew spawn
    crew_timer += 1
    if crew_timer >= crew_spawn_delay:
        crew.append(spawn_crew())
        crew_timer = 0

    move_crew()
    check_rescue()

    draw_ship()
    draw_crew()

    # HUD
    state_surf = font.render(f"State: {player_state}", True, WHITE)
    score_surf = font.render(f"Score: {score}", True, WHITE)
    screen.blit(state_surf, (10, 10))
    screen.blit(score_surf, (10, 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

