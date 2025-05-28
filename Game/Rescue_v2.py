import pygame
import random
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
FPS = 30

# Quantum States
STATES = ["|0>", "|1>", "|+>", "|->"]

# Initialize
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Quantum Rescue: Schrödinger's Crew")
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

# rocket_img = pygame.image.load(os.path.join("assets", "rocket.png"))
# rocket_img = pygame.transform.scale(rocket_img, (10, 4))
rocket_img = pygame.Surface((10, 4))
rocket_img.fill((255, 0, 0))

bullet_img = pygame.image.load(os.path.join("assets", "bullet.png"))
bullet_img = pygame.transform.scale(bullet_img, (25, 25))

powerup_img = pygame.image.load(os.path.join("assets", "powerup.png"))
powerup_img = pygame.transform.scale(powerup_img, (20, 20))

# Sounds
rescue_sound = pygame.mixer.Sound(os.path.join("assets", "rescue.wav"))
eliminate_sound = pygame.mixer.Sound(os.path.join("assets", "explode.wav"))

# Ship
ship = pygame.Rect(100, SCREEN_HEIGHT // 2, 60, 40)
ship_state = "|0>"
quantum_mode = False
score = 0
health = 100

# Crew Members
crew_members = []
CREW_INTERVAL = 60
crew_timer = 0

# Hazards
hazards = []
HAZARD_INTERVAL = 90
hazard_timer = 0

# Intruders
intruders = []
INTRUDER_INTERVAL = 70
intruder_timer = 0
intruder_bullets = []

# Rockets
rockets = []

# Power-ups
powerups = []
POWERUP_INTERVAL = 400
powerup_timer = 0

# Message
message = ""
message_timer = 0

# Colors
colors = {
    "|0>": (0, 255, 0),
    "|1>": (0, 0, 255),
    "|+>": (255, 255, 0),
    "|->": (255, 0, 255)
}

def apply_gate(gate):
    global ship_state, quantum_mode, message, message_timer
    if gate == "X" and not quantum_mode:
        ship_state = "|1>" if ship_state == "|0>" else "|0>"
    elif gate == "Z" and quantum_mode:
        ship_state = "|->" if ship_state == "|+>" else "|+>"
    elif gate == "H":
        if ship_state == "|0>":
            ship_state = "|+>"
            quantum_mode = True
        elif ship_state == "|1>":
            ship_state = "|->"
            quantum_mode = True
        elif ship_state == "|+>":
            ship_state = "|0>"
            quantum_mode = False
        elif ship_state == "|->":
            ship_state = "|1>"
            quantum_mode = False
    message = f"{gate} gate applied"
    message_timer = 60

running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        ship.move_ip(0, -5)
    if keys[pygame.K_DOWN]:
        ship.move_ip(0, 5)
    if keys[pygame.K_LEFT]:
        ship.move_ip(-5, 0)
    if keys[pygame.K_RIGHT]:
        ship.move_ip(5, 0)
    if keys[pygame.K_x]:
        apply_gate("X")
    if keys[pygame.K_z]:
        apply_gate("Z")
    if keys[pygame.K_h]:
        apply_gate("H")
    if keys[pygame.K_SPACE]:
        rockets.append(pygame.Rect(ship.centerx, ship.centery - 2, 10, 4))

    # Random gate application
    rand = random.randint(0, 300)
    if rand in [100, 200]:
        apply_gate("X")
    elif rand in [50, 250]:
        apply_gate("Z")
    elif rand == 150:
        apply_gate("H")

    # Constrain ship
    ship.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    # Spawn crew
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
        if random.random() < 0.7:
            intruder_bullets.append(pygame.Rect(rect.left, rect.centery, 6, 4))
        intruder_timer = 0

    # Spawn power-ups
    powerup_timer += 1
    if powerup_timer >= POWERUP_INTERVAL:
        y = random.randint(0, SCREEN_HEIGHT - 20)
        powerups.append(pygame.Rect(SCREEN_WIDTH, y, 20, 20))
        powerup_timer = 0

    # Update positions
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
        bullet.move_ip(-8, 0)
        if bullet.right < 0:
            intruder_bullets.remove(bullet)
    for powerup in powerups[:]:
        powerup.move_ip(-3, 0)

    # Check collisions
    for crew in crew_members[:]:
        if ship.colliderect(crew["rect"]):
            if crew["state"] == ship_state:
                crew_members.remove(crew)
                score += 1
                rescue_sound.play()
                message = "Crew rescued!"
                message_timer = 60
            else:
                # Gates flipped, crew acts as hazard
                crew_members.remove(crew)
                health -= 20
                message = "Hit by crew hazard!"
                message_timer = 60

    for hazard in hazards[:]:
        if ship.colliderect(hazard):
            hazards.remove(hazard)
            health -= 20
            message = "Hit by hazard!"
            message_timer = 60

    for intruder in intruders[:]:
        if ship.colliderect(intruder):
            health -= 40
            message = "Collided with intruder!"
            message_timer = 60
        for rocket in rockets[:]:
            if rocket.colliderect(intruder):
                intruders.remove(intruder)
                rockets.remove(rocket)
                eliminate_sound.play()
                message = "Intruder eliminated!"
                message_timer = 30
                break

    for bullet in intruder_bullets[:]:
        if ship.colliderect(bullet):
            intruder_bullets.remove(bullet)
            health -= 10
            message = "Hit by bullet!"
            message_timer = 60

    for powerup in powerups[:]:
        if ship.colliderect(powerup):
            powerups.remove(powerup)
            health = min(health + 30, 100)
            message = "Power-up collected!"
            message_timer = 60

    if health <= 0:
        message = "Game Over!"
        message_timer = 120
        running = False

    # Draw ship
    screen.blit(spaceship_img, ship)

    # Draw crew or hazard image depending on gate flips
    for crew in crew_members:
        if quantum_mode:
            # When gates flipped, crew acts as hazard visually
            screen.blit(hazard_img, crew["rect"])
        else:
            screen.blit(crew_img, crew["rect"])

    # Draw hazards
    for hazard in hazards:
        screen.blit(hazard_img, hazard)

    # Draw intruders
    for intruder in intruders:
        screen.blit(intruder_img, intruder)

    # Draw intruder bullets
    for bullet in intruder_bullets:
        screen.blit(bullet_img, bullet)

    # Draw rockets
    for rocket in rockets:
        screen.blit(rocket_img, rocket)

    # Draw power-ups with image
    for powerup in powerups:
        screen.blit(powerup_img, powerup)

    # Draw UI
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    state_text = font.render(f"State: {ship_state}", True, colors[ship_state])
    screen.blit(state_text, (10, 40))
    health_text = font.render(f"Health: {health}", True, (255, 0, 0))
    screen.blit(health_text, (10, 70))
    if message_timer > 0:
        msg = font.render(message, True, (255, 255, 255))
        screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 - msg.get_height()//2))
        message_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
