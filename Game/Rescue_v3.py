import pygame
import random
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
FPS = 30

# Quantum States
STATES = ["|0>", "|1>", "|+>", "|->"]

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Photonic Ship: Quantum Rescue")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# Load images
spaceship_img = pygame.image.load(os.path.join("assets", "spaceship.png"))
spaceship_img = pygame.transform.scale(spaceship_img, (60, 40))

crew_img = pygame.image.load(os.path.join("assets", "crew.png"))
crew_img = pygame.transform.scale(crew_img, (20, 20))

hazard_img = pygame.image.load(os.path.join("assets", "hazard.png"))
hazard_img = pygame.transform.scale(hazard_img, (20, 20))

intruder_img = pygame.image.load(os.path.join("assets", "intruder.png"))
intruder_img = pygame.transform.scale(intruder_img, (60, 40))

bullet_img = pygame.image.load(os.path.join("assets", "bullet.png"))
bullet_img = pygame.transform.scale(bullet_img, (25, 25))

powerup_img = pygame.image.load(os.path.join("assets", "powerup.png"))
powerup_img = pygame.transform.scale(powerup_img, (20, 20))

# Sounds
rescue_sound = pygame.mixer.Sound(os.path.join("assets", "rescue.wav"))
eliminate_sound = pygame.mixer.Sound(os.path.join("assets", "explode.wav"))

# Ship class to handle ship and twinship
class Ship:
    def __init__(self, x, y, state="|0>"):
        self.rect = pygame.Rect(x, y, 60, 40)
        self.state = state
        self.quantum_mode = False
        self.twinship = None
        self.health = 100

    def update_position(self, dy):
        # Move ship vertically within its half-screen
        if self.state == "|0>":
            if 0 <= self.rect.top + dy < SCREEN_HEIGHT // 2 - self.rect.height:
                self.rect.top += dy
        elif self.state == "|1>":
            if SCREEN_HEIGHT // 2 <= self.rect.top + dy < SCREEN_HEIGHT - self.rect.height:
                self.rect.top += dy

    def draw(self, surface):
        surface.blit(spaceship_img, self.rect)

    def create_twinship(self):
        # Create twinship on opposite half screen in superposition
        if self.state == "|+>":
            twin_y = SCREEN_HEIGHT // 2 + (self.rect.top % (SCREEN_HEIGHT // 2))
            self.twinship = Ship(self.rect.left, twin_y, "|->")
            self.quantum_mode = True
        elif self.state == "|->":
            twin_y = self.rect.top % (SCREEN_HEIGHT // 2)
            self.twinship = Ship(self.rect.left, twin_y, "|+>")
            self.quantum_mode = True
        else:
            self.twinship = None
            self.quantum_mode = False

    def remove_twinship(self):
        self.twinship = None
        self.quantum_mode = False

# Initialize main ship in upper half, |0> state
ship = Ship(100, SCREEN_HEIGHT // 4, "|0>")

# Game variables
score = 0
message = ""
message_timer = 0

# Enemies and objects
crew_members = []
CREW_INTERVAL = 60
crew_timer = 0

hazards = []
HAZARD_INTERVAL = 90
hazard_timer = 0

intruders = []
INTRUDER_INTERVAL = 70
intruder_timer = 0
intruder_bullets = []

rockets = []

powerups = []
POWERUP_INTERVAL = 400
powerup_timer = 0

# Colors for states
colors = {
    "|0>": (0, 255, 0),
    "|1>": (0, 0, 255),
    "|+>": (255, 255, 0),
    "|->": (255, 0, 255)
}

def apply_gate(gate):
    global message, message_timer
    # Apply gates based on current state and quantum mode
    if gate == "X":
        # X flips |0> <-> |1>, no effect in quantum mode
        if not ship.quantum_mode:
            if ship.state == "|0>":
                ship.state = "|1>"
                ship.rect.top = SCREEN_HEIGHT // 2 + 10
            elif ship.state == "|1>":
                ship.state = "|0>"
                ship.rect.top = 10
            message = "X gate applied"
            message_timer = 60
    elif gate == "Z":
        # Z flips |+> <-> |->, no effect in classic mode
        if ship.quantum_mode:
            if ship.state == "|+>":
                ship.state = "|->"
            elif ship.state == "|->":
                ship.state = "|+>"
            # Update twinship accordingly
            ship.create_twinship()
            message = "Z gate applied"
            message_timer = 60
    elif gate == "H":
        # H toggles between classic and quantum states
        if ship.state == "|0>":
            ship.state = "|+>"
            ship.create_twinship()
        elif ship.state == "|1>":
            ship.state = "|->"
            ship.create_twinship()
        elif ship.state == "|+>":
            ship.state = "|0>"
            ship.remove_twinship()
            ship.rect.top = 10
        elif ship.state == "|->":
            ship.state = "|1>"
            ship.remove_twinship()
            ship.rect.top = SCREEN_HEIGHT // 2 + 10
        message = "H gate applied"
        message_timer = 60

def measure():
    global message, message_timer, running
    # Measurement collapses superposition into classical state randomly
    if ship.quantum_mode:
        # Pick random int 1-100, even -> |0>, odd -> |1>
        observed = "|0>" if random.randint(1, 100) % 2 == 0 else "|1>"
        ship.state = observed
        # Set position accordingly
        if observed == "|0>":
            ship.rect.top = 10
        else:
            ship.rect.top = SCREEN_HEIGHT // 2 + 10
        ship.remove_twinship()
        ship.quantum_mode = False
        message = f"Measurement: collapsed to {observed}"
        message_timer = 120

        # Check collisions again after collapse, if hit then game over
        if check_collision_after_measure():
            message += " - Ship destroyed!"
            message_timer = 120
            return True  # Game over
        else:
            message += " - Ship survived!"
            message_timer = 120
            return False
    return False

def check_collision_after_measure():
    # Check collision after measurement collapse
    # Just check if ship hits hazards or intruders immediately
    for hazard in hazards:
        if ship.rect.colliderect(hazard):
            return True
    for intruder in intruders:
        if ship.rect.colliderect(intruder):
            return True
    for bullet in intruder_bullets:
        if ship.rect.colliderect(bullet):
            return True
    return False

running = True
while running:
    screen.fill((0, 0, 0))

    # Draw center line splitting the screen into |0> and |1>
    pygame.draw.line(screen, (255, 255, 255), (0, SCREEN_HEIGHT//2), (SCREEN_WIDTH, SCREEN_HEIGHT//2), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Movement and gates input only if not in quantum mode or allowed
    if not ship.quantum_mode:
        # Move ship up/down within its screen half
        if keys[pygame.K_UP]:
            ship.update_position(-5)
        if keys[pygame.K_DOWN]:
            ship.update_position(5)
    else:
        # In quantum mode, arrow keys move enemies only
        if keys[pygame.K_UP]:
            for enemy in hazards + intruders + crew_members:
                enemy_rect = enemy if isinstance(enemy, pygame.Rect) else enemy['rect']
                enemy_rect.top -= 5
                # Wrap around vertical screen
                if enemy_rect.top < 0:
                    enemy_rect.top = SCREEN_HEIGHT - enemy_rect.height
        if keys[pygame.K_DOWN]:
            for enemy in hazards + intruders + crew_members:
                enemy_rect = enemy if isinstance(enemy, pygame.Rect) else enemy['rect']
                enemy_rect.top += 5
                # Wrap around vertical screen
                if enemy_rect.top > SCREEN_HEIGHT - enemy_rect.height:
                    enemy_rect.top = 0

    # Gates
    if keys[pygame.K_x]:
        apply_gate("X")
    if keys[pygame.K_z]:
        apply_gate("Z")
    if keys[pygame.K_h]:
        apply_gate("H")

    # Random gate application as per Task 8
    rand = random.randint(0, 300)
    if rand in [100, 200]:
        apply_gate("X")
    elif rand in [50, 250]:
        apply_gate("Z")
    elif rand == 150:
        apply_gate("H")

    # Spawn crew members
    crew_timer += 1
    if crew_timer >= CREW_INTERVAL:
        crew_state = random.choice(STATES)
        y = random.randint(0, SCREEN_HEIGHT - 20)
        crew_members.append({"rect": pygame.Rect(SCREEN_WIDTH, y, 20, 20), "state": crew_state})
        crew_timer = 0

    # Spawn hazards
    hazard_timer += 1
    if hazard_timer >= HAZARD_INTERVAL:
        y = random.randint(0, SCREEN_HEIGHT - 20)
        hazards.append(pygame.Rect(SCREEN_WIDTH, y, 20, 20))
        hazard_timer = 0

    # Spawn intruders
    intruder_timer += 1
    if intruder_timer >= INTRUDER_INTERVAL:
        y = random.randint(0, SCREEN_HEIGHT - 40)
        rect = pygame.Rect(SCREEN_WIDTH, y, 60, 40)
        intruders.append(rect)
        # Intruder fires bullet sometimes
        if random.random() < 0.7:
            intruder_bullets.append(pygame.Rect(rect.left, rect.centery, 6, 4))
        intruder_timer = 0

    # Spawn power-ups
    powerup_timer += 1
    if powerup_timer >= POWERUP_INTERVAL:
        y = random.randint(0, SCREEN_HEIGHT - 20)
        powerups.append(pygame.Rect(SCREEN_WIDTH, y, 20, 20))
        powerup_timer = 0

    # Move all enemies and objects leftwards
    for crew in crew_members:
        crew["rect"].move_ip(-5, 0)
    for hazard in hazards:
        hazard.move_ip(-8, 0)
    for intruder in intruders:
        intruder.move_ip(-6, 0)
    for rocket in rockets[:]:
        rocket.move_ip(10, 0)
        if rocket.left > SCREEN_WIDTH:
            rockets.remove(rocket)
    for bullet in intruder_bullets[:]:
        bullet.move_ip(-10, 0)
        if bullet.right < 0:
            intruder_bullets.remove(bullet)
    for powerup in powerups:
        powerup.move_ip(-4, 0)

    # Remove off-screen objects
    crew_members = [c for c in crew_members if c["rect"].right > 0]
    hazards = [h for h in hazards if h.right > 0]
    intruders = [i for i in intruders if i.right > 0]
    powerups = [p for p in powerups if p.right > 0]

    # Draw crew
    for crew in crew_members:
        img = crew_img
        screen.blit(img, crew["rect"])

    # Draw hazards
    for hazard in hazards:
        screen.blit(hazard_img, hazard)

    # Draw intruders
    for intruder in intruders:
        screen.blit(intruder_img, intruder)
    for bullet in intruder_bullets:
        screen.blit(bullet_img, bullet)

    # Draw powerups
    for powerup in powerups:
        screen.blit(powerup_img, powerup)

    # Draw ship and twinship
    ship.draw(screen)
    if ship.twinship:
        ship.twinship.draw(screen)

    # Collision detection
    # Check if ship or twinship collides with hazards or intruders
    def collision_check():
        for hazard in hazards:
            if ship.rect.colliderect(hazard):
                return True
            if ship.twinship and ship.twinship.rect.colliderect(hazard):
                return True
        for intruder in intruders:
            if ship.rect.colliderect(intruder):
                return True
            if ship.twinship and ship.twinship.rect.colliderect(intruder):
                return True
        for bullet in intruder_bullets:
            if ship.rect.colliderect(bullet):
                return True
            if ship.twinship and ship.twinship.rect.colliderect(bullet):
                return True
        return False

    if ship.quantum_mode:
        # If collision in superposition, measure collapse and check result
        if collision_check():
            game_over = measure()
            if game_over:
                message = "Game Over!"
                running = False
    else:
        if collision_check():
            message = "Game Over!"
            running = False

    # Display state on top-right corner
    state_text = font.render(f"State: {ship.state}", True, colors.get(ship.state, (255, 255, 255)))
    screen.blit(state_text, (SCREEN_WIDTH - 180, 10))

    # Display message if any
    if message_timer > 0:
        msg_surface = font.render(message, True, (255, 255, 255))
        screen.blit(msg_surface, (20, SCREEN_HEIGHT - 40))
        message_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
