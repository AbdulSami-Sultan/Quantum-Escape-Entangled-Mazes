import pygame
import random
import os

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Quantum States
CLASSICAL_STATES = ["|0>", "|1>"]
SUPERPOSITION_STATES = ["|+>", "|->"]

# Initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quantum Bubble Burst")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Load assets
background_img = pygame.image.load(os.path.join("assets", "background.png"))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

bubble_img = pygame.image.load(os.path.join("assets", "bubble.png"))
bubble_img = pygame.transform.scale(bubble_img, (40, 40))

super_bubble_img = pygame.image.load(os.path.join("assets", "super_bubble.png"))
super_bubble_img = pygame.transform.scale(super_bubble_img, (40, 40))

burst_sound = pygame.mixer.Sound(os.path.join("assets", "rescue.wav"))

# Bubble class
class Bubble:
    def __init__(self, x, y, state):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.state = state
        self.superposition = state in SUPERPOSITION_STATES

    def draw(self, screen):
        if self.superposition:
            screen.blit(super_bubble_img, self.rect)
        else:
            screen.blit(bubble_img, self.rect)

    def collapse(self):
        # Randomly collapse to |0> or |1>
        outcome = random.choice(CLASSICAL_STATES)
        self.state = outcome
        self.superposition = False

# Game variables
bubbles = []
score = 0
message = ""
message_timer = 0

# Gate control
def apply_gate(bubble, gate):
    if gate == "H":
        if bubble.state in CLASSICAL_STATES:
            bubble.state = "|+>" if bubble.state == "|0>" else "|->"
            bubble.superposition = True
        elif bubble.state in SUPERPOSITION_STATES:
            bubble.state = "|0>" if bubble.state == "|+>" else "|1>"
            bubble.superposition = False
    elif gate == "X":
        if bubble.state in CLASSICAL_STATES:
            bubble.state = "|1>" if bubble.state == "|0>" else "|0>"
    elif gate == "Z":
        if bubble.state == "|+>":
            bubble.state = "|->"
        elif bubble.state == "|->":
            bubble.state = "|+>"

# Bubble spawning
SPAWN_INTERVAL = 60
spawn_timer = 0

# Main loop
running = True
while running:
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:  # Apply Hadamard to all bubbles
        for b in bubbles:
            apply_gate(b, "H")
    if keys[pygame.K_x]:
        for b in bubbles:
            apply_gate(b, "X")
    if keys[pygame.K_z]:
        for b in bubbles:
            apply_gate(b, "Z")

    # Mouse click = burst bubble
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        for b in bubbles[:]:
            if b.rect.collidepoint(mx, my):
                if b.superposition:
                    b.collapse()
                    if random.choice([True, False]):
                        burst_sound.play()
                        bubbles.remove(b)
                        score += 10
                        message = "Quantum collapse: Bubble burst!"
                        message_timer = 60
                else:
                    burst_sound.play()
                    bubbles.remove(b)
                    score += 10
                    message = "Bubble burst!"
                    message_timer = 60
                    # Chain reaction: burst neighbors
                    for nb in bubbles[:]:
                        if nb.rect.colliderect(b.rect.inflate(60, 60)) and nb != b:
                            if not nb.superposition:
                                bubbles.remove(nb)
                                burst_sound.play()
                                score += 5

    # Spawn new bubbles
    spawn_timer += 1
    if spawn_timer >= SPAWN_INTERVAL:
        x = random.randint(0, WIDTH - 40)
        y = random.randint(0, HEIGHT - 40)
        state = random.choice(CLASSICAL_STATES + SUPERPOSITION_STATES)
        bubbles.append(Bubble(x, y, state))
        spawn_timer = 0

    # Draw bubbles
    for b in bubbles:
        b.draw(screen)

    # Display score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Display message
    if message_timer > 0:
        msg_text = font.render(message, True, (255, 255, 255))
        screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT // 2))
        message_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
